// BarBridge.cs — NinjaScript Indicator
// Writes each bar close to CSV for live_runner to read
// 
// Setup:
// 1. Open NinjaScript Editor (Tools → Edit NinjaScript → Indicator)
// 2. Create new indicator, paste this code
// 3. Compile (F5)
// 4. Add to chart

#region Using declarations
using System;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using Cbi;
using Ninjatrader.Cbi;
using Ninjatrader.Gui;
using Ninjatrader.Gui.Tools;
using Ninjatrader.Data;
using Ninjatrader.NinjaScript;
using Ninjatrader.Core.FloatingPoint;
using Ninjatrader.Instrument;
#endregion

namespace Ninjatrader.NinjaScript.Indicators
{
    public class BarBridge : Indicator
    {
        private string csvPath = @"data\live\MES_1m.csv";
        private System.IO.StreamWriter csvWriter;
        private bool headerWritten = false;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Write bars to CSV for live_runner";
                Name = "BarBridge";
                IsOverlay = false;
                IsSuspendedWhileInactive = false;
            }
            else if (State == State.Configure)
            {
                AddPlot(Brushes.Transparent, "Dummy");
            }
            else if (State == State.DataLoaded)
            {
                // Create directory if it doesn't exist
                string dir = System.IO.Path.GetDirectoryName(csvPath);
                if (!System.IO.Directory.Exists(dir))
                    System.IO.Directory.CreateDirectory(dir);

                // Clear existing file
                if (System.IO.File.Exists(csvPath))
                    System.IO.File.Delete(csvPath);

                // Open CSV writer
                csvWriter = new System.IO.StreamWriter(csvPath, false);
                Print($"BarBridge: Writing to {csvPath}");
            }
        }

        protected override void OnBarClose()
        {
            try
            {
                // Write header on first bar
                if (!headerWritten)
                {
                    csvWriter.WriteLine("time,open,high,low,close,volume");
                    csvWriter.Flush();
                    headerWritten = true;
                }

                // Write bar data
                string line = string.Format("{0:yyyy-MM-dd HH:mm:ss},{1},{2},{3},{4},{5}",
                    Time[0],
                    Open[0],
                    High[0],
                    Low[0],
                    Close[0],
                    Volume[0]);

                csvWriter.WriteLine(line);
                csvWriter.Flush();

                Print($"BarBridge: {line}");
            }
            catch (Exception e)
            {
                Print($"BarBridge ERROR: {e.Message}");
            }
        }

        protected override void OnTermination()
        {
            if (csvWriter != null)
            {
                csvWriter.Close();
                csvWriter.Dispose();
            }
        }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace Ninjatrader.NinjaScript.Indicators
{
    public partial class Indicator : Ninjatrader.Cbi.Indicator
    {
        private BarBridge[] cacheBarBridge;

        public BarBridge BarBridge()
        {
            return BarBridge(Close);
        }

        public BarBridge BarBridge(ISeries<double> input)
        {
            if (cacheBarBridge != null)
                for (int idx = 0; idx < cacheBarBridge.Length; idx++)
                    if (cacheBarBridge[idx] != null && cacheBarBridge[idx].EqualsInput(input))
                        return cacheBarBridge[idx];
            return CacheIndicator<BarBridge>(new BarBridge() { Input = input }, ref cacheBarBridge);
        }
    }
}

namespace Ninjatrader.Cbi
{
    public partial class Instrument
    {
        public Ninjatrader.NinjaScript.Indicators.BarBridge BarBridge()
        {
            return Ninjatrader.NinjaScript.Indicators.BarBridge(Close);
        }

        public Ninjatrader.NinjaScript.Indicators.BarBridge BarBridge(ISeries<double> input)
        {
            return Ninjatrader.NinjaScript.Indicators.BarBridge(input);
        }
    }
}

#endregion
