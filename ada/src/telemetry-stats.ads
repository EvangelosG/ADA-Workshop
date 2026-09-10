--  Generics: the aggregation is written once and instantiated per selector.
package Telemetry.Stats is

   type Summary is record
      Count   : Natural;
      Minimum : Celsius;
      Maximum : Celsius;
      Mean    : Celsius;
   end record;

   --  Only readings whose quality is Good take part in the summary.
   --  Raises Invalid_Reading when no reading qualifies.
   function Summarise (Data : Reading_Array) return Summary;

   generic
      with function Selected (Item : Reading) return Boolean;
   function Count_Where (Data : Reading_Array) return Natural;

end Telemetry.Stats;
