with Ada.Strings.Fixed;

package body Telemetry.Parsing is

   use Ada.Strings.Fixed;

   type Field_Array is array (1 .. 4) of Natural;

   --  Positions of the three separating commas plus the end of the line.
   function Field_Ends (Line : String) return Field_Array is
      Result : Field_Array := (others => 0);
      Found  : Natural := 0;
   begin
      for Index in Line'Range loop
         if Line (Index) = ',' then
            Found := Found + 1;
            if Found > 3 then
               raise Invalid_Reading with "too many fields: " & Line;
            end if;
            Result (Found) := Index;
         end if;
      end loop;
      if Found /= 3 then
         raise Invalid_Reading with "expected 4 fields: " & Line;
      end if;
      Result (4) := Line'Last + 1;
      return Result;
   end Field_Ends;

   function To_Natural (Text : String; Line : String) return Natural is
      Value : Natural := 0;
   begin
      if Text'Length = 0 then
         raise Invalid_Reading with "empty number: " & Line;
      end if;
      for Index in Text'Range loop
         if Text (Index) not in '0' .. '9' then
            raise Invalid_Reading with "not a number: " & Line;
         end if;
         Value := Value * 10 + (Character'Pos (Text (Index))
                                - Character'Pos ('0'));
      end loop;
      return Value;
   end To_Natural;

   --  "-12.3" and "7" are both accepted; the result is scaled to tenths.
   function To_Tenths (Text : String; Line : String) return Integer is
      Negative : constant Boolean := Text'Length > 0
        and then Text (Text'First) = '-';
      First    : constant Natural := (if Negative
                                      then Text'First + 1 else Text'First);
      Dot      : constant Natural := Index (Text (First .. Text'Last), ".");
      Whole    : Natural;
      Frac     : Natural := 0;
   begin
      if Dot = 0 then
         Whole := To_Natural (Text (First .. Text'Last), Line);
      else
         Whole := To_Natural (Text (First .. Dot - 1), Line);
         if Dot + 1 /= Text'Last then
            raise Invalid_Reading with "expected one decimal: " & Line;
         end if;
         Frac := To_Natural (Text (Dot + 1 .. Text'Last), Line);
      end if;
      return (if Negative then -1 else 1) * (Whole * 10 + Frac);
   end To_Tenths;

   function To_Quality (Text : String; Line : String) return Quality is
   begin
      if Text = "G" then
         return Good;
      elsif Text = "S" then
         return Suspect;
      elsif Text = "B" then
         return Bad;
      else
         raise Invalid_Reading with "unknown quality: " & Line;
      end if;
   end To_Quality;

   function Parse_Line (Line : String) return Reading is
      Ends   : constant Field_Array := Field_Ends (Line);
      Raw_Id : constant Natural :=
        To_Natural (Trim (Line (Line'First .. Ends (1) - 1),
                          Ada.Strings.Both), Line);
      Raw_T  : constant Natural :=
        To_Natural (Trim (Line (Ends (1) + 1 .. Ends (2) - 1),
                          Ada.Strings.Both), Line);
      Tenths : constant Integer :=
        To_Tenths (Trim (Line (Ends (2) + 1 .. Ends (3) - 1),
                         Ada.Strings.Both), Line);
      State  : constant Quality :=
        To_Quality (Trim (Line (Ends (3) + 1 .. Ends (4) - 1),
                          Ada.Strings.Both), Line);
   begin
      if Raw_Id < 1 or else Raw_Id > 99 then
         raise Invalid_Reading with "sensor id out of range: " & Line;
      end if;
      if Raw_T > 86_399 then
         raise Invalid_Reading with "timestamp out of range: " & Line;
      end if;
      if Tenths < -800 or else Tenths > 1_500 then
         raise Invalid_Reading with "temperature out of range: " & Line;
      end if;

      return (Id    => Sensor_Id (Raw_Id),
              Time  => Timestamp (Raw_T),
              Value => Celsius'(0.1) * Tenths,
              State => State);
   end Parse_Line;

   function Is_Skippable (Line : String) return Boolean is
      Stripped : constant String := Trim (Line, Ada.Strings.Both);
   begin
      return Stripped'Length = 0 or else Stripped (Stripped'First) = '#';
   end Is_Skippable;

end Telemetry.Parsing;
