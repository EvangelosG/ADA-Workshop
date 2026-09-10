--  Text handling: turn "id,time,value,quality" lines into readings.
package Telemetry.Parsing is

   --  Raises Invalid_Reading (with a message) on malformed or out of range
   --  input. The message text is part of the observable behaviour, so a
   --  migration has to reproduce it.
   function Parse_Line (Line : String) return Reading;

   --  Blank lines and lines starting with '#' are skipped.
   function Is_Skippable (Line : String) return Boolean;

end Telemetry.Parsing;
