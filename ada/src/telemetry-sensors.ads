--  Tagged types and dispatching: each sensor kind reports its own label and
--  applies its own calibration offset.
package Telemetry.Sensors is

   type Sensor is abstract tagged record
      Id    : Sensor_Id;
      Label : String (1 .. 12);
   end record;

   function Kind (Item : Sensor) return String is abstract;

   --  Primitive with a default implementation that derived types may override.
   function Calibrate (Item : Sensor; Raw : Celsius) return Celsius;

   function Describe (Item : Sensor'Class) return String;

   type Thermocouple is new Sensor with record
      Offset : Celsius;
   end record;

   overriding function Kind (Item : Thermocouple) return String;
   overriding function Calibrate
     (Item : Thermocouple; Raw : Celsius) return Celsius;

   type Thermistor is new Sensor with record
      Reference : Celsius;
   end record;

   overriding function Kind (Item : Thermistor) return String;
   overriding function Calibrate
     (Item : Thermistor; Raw : Celsius) return Celsius;

   type Sensor_Ref is access all Sensor'Class;
   type Sensor_Table is array (Positive range <>) of Sensor_Ref;

   --  Raises Invalid_Reading when no sensor with that id is registered.
   function Find (Table : Sensor_Table; Id : Sensor_Id) return Sensor_Ref;

end Telemetry.Sensors;
