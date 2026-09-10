--  Root package: shared domain types for the telemetry pipeline.
package Telemetry is

   --  Constrained integer subtype: values outside the range raise
   --  Constraint_Error at run time.
   type Sensor_Id is range 1 .. 99;

   type Timestamp is range 0 .. 86_399;

   --  Fixed point temperature with a resolution of one tenth of a degree.
   type Celsius is delta 0.1 digits 6 range -80.0 .. 150.0;

   type Quality is (Good, Suspect, Bad);

   type Reading is record
      Id    : Sensor_Id;
      Time  : Timestamp;
      Value : Celsius;
      State : Quality;
   end record;

   type Reading_Array is array (Positive range <>) of Reading;

   Invalid_Reading : exception;

   --  Deterministic textual form of a fixed point value, e.g. "-12.3".
   function Image (Value : Celsius) return String;

   function Image (Value : Sensor_Id) return String;

   function Image (Value : Timestamp) return String;

   function Image (Value : Natural) return String;

end Telemetry;
