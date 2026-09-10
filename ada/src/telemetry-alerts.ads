--  Discriminated (variant) records: one rule type, three shapes.
package Telemetry.Alerts is

   type Rule_Kind is (Above, Below, Stuck);

   type Rule (Kind : Rule_Kind := Above) is record
      Id : Sensor_Id;
      case Kind is
         when Above | Below =>
            Threshold : Celsius;
         when Stuck =>
            Window : Positive;
      end case;
   end record;

   type Rule_Array is array (Positive range <>) of Rule;

   type Alert is record
      Id      : Sensor_Id;
      Time    : Timestamp;
      Message : String (1 .. 40);
      Length  : Natural;
   end record;

   type Alert_Array is array (Positive range <>) of Alert;

   --  Evaluates every rule against every reading, in rule order then reading
   --  order. Count is the number of valid entries in the returned array.
   procedure Evaluate
     (Data  : Reading_Array;
      Rules : Rule_Array;
      Into  : out Alert_Array;
      Count : out Natural);

   function Text (Item : Alert) return String;

end Telemetry.Alerts;
