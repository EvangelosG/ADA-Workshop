package body Telemetry.Alerts is

   function Make_Alert
     (Id : Sensor_Id; Time : Timestamp; Message : String) return Alert
   is
      Result : Alert := (Id      => Id,
                         Time    => Time,
                         Message => (others => ' '),
                         Length  => 0);
      Last   : constant Natural :=
        Natural'Min (Message'Length, Result.Message'Length);
   begin
      Result.Message (1 .. Last) :=
        Message (Message'First .. Message'First + Last - 1);
      Result.Length := Last;
      return Result;
   end Make_Alert;

   function Text (Item : Alert) return String is
   begin
      return Item.Message (1 .. Item.Length);
   end Text;

   --  A stuck sensor reports the same value for Window consecutive readings.
   function Is_Stuck
     (Data : Reading_Array; At_Index : Positive; Id : Sensor_Id;
      Window : Positive) return Boolean
   is
      Seen : Natural := 0;
   begin
      for Index in reverse Data'First .. At_Index loop
         if Data (Index).Id = Id then
            if Data (Index).Value /= Data (At_Index).Value then
               return False;
            end if;
            Seen := Seen + 1;
            exit when Seen = Window;
         end if;
      end loop;
      return Seen = Window;
   end Is_Stuck;

   procedure Evaluate
     (Data  : Reading_Array;
      Rules : Rule_Array;
      Into  : out Alert_Array;
      Count : out Natural)
   is
   begin
      Count := 0;
      Into := (others => (Id      => Sensor_Id'First,
                          Time    => Timestamp'First,
                          Message => (others => ' '),
                          Length  => 0));

      for Rule_Index in Rules'Range loop
         declare
            Current : constant Rule := Rules (Rule_Index);
         begin
            for Index in Data'Range loop
               if Data (Index).Id = Current.Id
                 and then Data (Index).State /= Bad
               then
                  case Current.Kind is
                     when Above =>
                        if Data (Index).Value > Current.Threshold then
                           Count := Count + 1;
                           Into (Count) := Make_Alert
                             (Current.Id, Data (Index).Time,
                              "above " & Image (Current.Threshold)
                              & " (" & Image (Data (Index).Value) & ")");
                        end if;
                     when Below =>
                        if Data (Index).Value < Current.Threshold then
                           Count := Count + 1;
                           Into (Count) := Make_Alert
                             (Current.Id, Data (Index).Time,
                              "below " & Image (Current.Threshold)
                              & " (" & Image (Data (Index).Value) & ")");
                        end if;
                     when Stuck =>
                        if Is_Stuck (Data, Index, Current.Id, Current.Window)
                        then
                           Count := Count + 1;
                           Into (Count) := Make_Alert
                             (Current.Id, Data (Index).Time,
                              "stuck at " & Image (Data (Index).Value));
                        end if;
                  end case;
               end if;
            end loop;
         end;
      end loop;
   end Evaluate;

end Telemetry.Alerts;
