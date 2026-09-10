with Ada.Strings.Fixed;

package body Telemetry.Sensors is

   function Calibrate (Item : Sensor; Raw : Celsius) return Celsius is
      pragma Unreferenced (Item);
   begin
      return Raw;
   end Calibrate;

   function Describe (Item : Sensor'Class) return String is
      use Ada.Strings.Fixed;
   begin
      return Trim (Item.Label, Ada.Strings.Both)
        & " [" & Kind (Item) & "#" & Image (Item.Id) & "]";
   end Describe;

   overriding function Kind (Item : Thermocouple) return String is
      pragma Unreferenced (Item);
   begin
      return "thermocouple";
   end Kind;

   overriding function Calibrate
     (Item : Thermocouple; Raw : Celsius) return Celsius is
   begin
      return Raw + Item.Offset;
   end Calibrate;

   overriding function Kind (Item : Thermistor) return String is
      pragma Unreferenced (Item);
   begin
      return "thermistor";
   end Kind;

   --  A thermistor drifts towards its reference value; halve the deviation.
   overriding function Calibrate
     (Item : Thermistor; Raw : Celsius) return Celsius is
      Deviation : constant Celsius := Raw - Item.Reference;
   begin
      return Item.Reference + Celsius (Deviation / 2);
   end Calibrate;

   function Find (Table : Sensor_Table; Id : Sensor_Id) return Sensor_Ref is
   begin
      for Entry_Index in Table'Range loop
         if Table (Entry_Index) /= null
           and then Table (Entry_Index).Id = Id
         then
            return Table (Entry_Index);
         end if;
      end loop;
      raise Invalid_Reading with "unknown sensor id " & Image (Id);
   end Find;

end Telemetry.Sensors;
