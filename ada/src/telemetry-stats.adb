package body Telemetry.Stats is

   function Tenths (Value : Celsius) return Integer is
     (Integer (Value / Celsius'(0.1)));

   --  The mean is computed in tenths and truncated towards zero, so that the
   --  result never depends on floating point rounding.
   function Summarise (Data : Reading_Array) return Summary is
      Count : Natural := 0;
      Total : Integer := 0;
      Low   : Celsius := Celsius'Last;
      High  : Celsius := Celsius'First;
   begin
      for Index in Data'Range loop
         if Data (Index).State = Good then
            Count := Count + 1;
            Total := Total + Tenths (Data (Index).Value);
            if Data (Index).Value < Low then
               Low := Data (Index).Value;
            end if;
            if Data (Index).Value > High then
               High := Data (Index).Value;
            end if;
         end if;
      end loop;

      if Count = 0 then
         raise Invalid_Reading with "no good readings to summarise";
      end if;

      return (Count   => Count,
              Minimum => Low,
              Maximum => High,
              Mean    => Celsius'(0.1) * (Total / Count));
   end Summarise;

   function Count_Where (Data : Reading_Array) return Natural is
      Total : Natural := 0;
   begin
      for Index in Data'Range loop
         if Selected (Data (Index)) then
            Total := Total + 1;
         end if;
      end loop;
      return Total;
   end Count_Where;

end Telemetry.Stats;
