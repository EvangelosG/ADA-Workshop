package body Telemetry is

   --  Integer'Image prefixes non negative values with a blank; drop it so the
   --  report layout is under our control.
   function Trim (Value : Integer) return String is
      Raw : constant String := Integer'Image (Value);
   begin
      if Raw (Raw'First) = ' ' then
         return Raw (Raw'First + 1 .. Raw'Last);
      else
         return Raw;
      end if;
   end Trim;

   function Image (Value : Celsius) return String is
      Tenths : constant Integer := Integer (Value / Celsius'(0.1));
      Sign   : constant String  := (if Tenths < 0 then "-" else "");
      Mag    : constant Integer := abs Tenths;
      Whole  : constant Integer := Mag / 10;
      Frac   : constant Integer := Mag mod 10;
   begin
      return Sign & Trim (Whole) & "." & Trim (Frac);
   end Image;

   function Image (Value : Sensor_Id) return String is
   begin
      return Trim (Integer (Value));
   end Image;

   function Image (Value : Timestamp) return String is
   begin
      return Trim (Integer (Value));
   end Image;

   function Image (Value : Natural) return String is
   begin
      return Trim (Integer (Value));
   end Image;

end Telemetry;
