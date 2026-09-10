with Ada.Command_Line;
with Ada.Exceptions;
with Ada.Text_IO;

with Telemetry;
with Telemetry.Alerts;
with Telemetry.Parsing;
with Telemetry.Sensors;
with Telemetry.Stats;

--  Reads a readings file and prints a deterministic report on standard
--  output. Exit status is 0 on success and 2 on a rejected input file.
procedure Telemetry_Main is

   use Ada.Text_IO;
   use Telemetry;

   Max_Readings : constant := 256;

   Probe_A : aliased Telemetry.Sensors.Thermocouple :=
     (Id => 7, Label => "boiler-inlet", Offset => 1.5);
   Probe_B : aliased Telemetry.Sensors.Thermistor :=
     (Id => 12, Label => "cabin-air   ", Reference => 20.0);
   Probe_C : aliased Telemetry.Sensors.Thermocouple :=
     (Id => 31, Label => "exhaust     ", Offset => -2.0);

   Table : constant Telemetry.Sensors.Sensor_Table :=
     (Probe_A'Unchecked_Access, Probe_B'Unchecked_Access,
      Probe_C'Unchecked_Access);

   Rules : constant Telemetry.Alerts.Rule_Array :=
     ((Kind => Telemetry.Alerts.Above, Id => 7, Threshold => 90.0),
      (Kind => Telemetry.Alerts.Below, Id => 12, Threshold => 18.0),
      (Kind => Telemetry.Alerts.Stuck, Id => 31, Window => 3));

   function Is_Suspect (Item : Reading) return Boolean is
     (Item.State = Suspect);

   function Count_Suspect is
     new Telemetry.Stats.Count_Where (Selected => Is_Suspect);

   Data  : Reading_Array (1 .. Max_Readings);
   Count : Natural := 0;

   procedure Load (Path : String) is
      File : File_Type;
   begin
      Open (File, In_File, Path);
      while not End_Of_File (File) loop
         declare
            Line : constant String := Get_Line (File);
         begin
            if not Telemetry.Parsing.Is_Skippable (Line) then
               if Count = Max_Readings then
                  raise Invalid_Reading with "too many readings";
               end if;
               Count := Count + 1;
               Data (Count) := Telemetry.Parsing.Parse_Line (Line);
            end if;
         end;
      end loop;
      Close (File);
   end Load;

   procedure Report is
      Calibrated : Reading_Array (1 .. Count);
      Alerts     : Telemetry.Alerts.Alert_Array (1 .. Max_Readings);
      Alert_Count : Natural;
   begin
      for Index in 1 .. Count loop
         declare
            Item   : constant Reading := Data (Index);
            Sensor : constant Telemetry.Sensors.Sensor_Ref :=
              Telemetry.Sensors.Find (Table, Item.Id);
         begin
            Calibrated (Index) :=
              (Id    => Item.Id,
               Time  => Item.Time,
               Value => Telemetry.Sensors.Calibrate (Sensor.all, Item.Value),
               State => Item.State);
         end;
      end loop;

      Put_Line ("TELEMETRY REPORT");
      Put_Line ("================");
      Put_Line ("readings: " & Image (Count));

      Put_Line ("");
      Put_Line ("sensors:");
      for Index in Table'Range loop
         Put_Line ("  " & Telemetry.Sensors.Describe (Table (Index).all));
      end loop;

      Put_Line ("");
      Put_Line ("calibrated summary (good readings only):");
      declare
         Result : constant Telemetry.Stats.Summary :=
           Telemetry.Stats.Summarise (Calibrated);
      begin
         Put_Line ("  count: " & Image (Result.Count));
         Put_Line ("  min:   " & Image (Result.Minimum));
         Put_Line ("  max:   " & Image (Result.Maximum));
         Put_Line ("  mean:  " & Image (Result.Mean));
      end;
      Put_Line ("  suspect readings: " & Image (Count_Suspect (Calibrated)));

      Put_Line ("");
      Put_Line ("alerts:");
      Telemetry.Alerts.Evaluate (Calibrated, Rules, Alerts, Alert_Count);
      if Alert_Count = 0 then
         Put_Line ("  none");
      else
         for Index in 1 .. Alert_Count loop
            Put_Line ("  t=" & Image (Alerts (Index).Time)
                      & " sensor " & Image (Alerts (Index).Id)
                      & ": " & Telemetry.Alerts.Text (Alerts (Index)));
         end loop;
      end if;
   end Report;

begin
   if Ada.Command_Line.Argument_Count /= 1 then
      Put_Line (Standard_Error, "usage: telemetry_main <readings-file>");
      Ada.Command_Line.Set_Exit_Status (2);
      return;
   end if;

   Load (Ada.Command_Line.Argument (1));
   Report;

exception
   when Error : Invalid_Reading =>
      Put_Line (Standard_Error,
                "rejected: " & Ada.Exceptions.Exception_Message (Error));
      Ada.Command_Line.Set_Exit_Status (2);
   when Error : others =>
      Put_Line (Standard_Error,
                "failed: " & Ada.Exceptions.Exception_Name (Error));
      Ada.Command_Line.Set_Exit_Status (2);
end Telemetry_Main;
