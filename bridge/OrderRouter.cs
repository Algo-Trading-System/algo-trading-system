// OrderRouter.cs — NinjaScript Strategy
// Listens for HTTP POST signals from live_runner, places orders via NT8 API
//
// Setup:
// 1. Open NinjaScript Editor (Tools → Edit NinjaScript → Strategy)
// 2. Create new strategy, paste this code
// 3. Compile (F5)
// 4. Add to chart (same chart as BarBridge)

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
using System.Net;
using System.IO;
#endregion

namespace Ninjatrader.NinjaScript.Strategies
{
    public class OrderRouter : Strategy
    {
        private HttpListener httpListener;
        private System.IO.StreamWriter logWriter;
        private string logPath = @"NT8-Logs\OrderRouter.log";

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
                Description = "Receive signals via HTTP, place orders";
                Name = "OrderRouter";
                Calculate = Calculate.OnBarClose;
                EntriesPerDirection = 1;
                EntryHandling = EntryHandling.AllEntries;
                IsExitOnSessionCloseStrategy = true;
                ExitOnSessionCloseSeconds = 30;
                IsFillLimitOnTouch = false;
                MaximumBarsLookBack = BarLookBack.TwoBarsAgo;
                OrderFillResolution = OrderFillResolution.Standard;
                Slippage = 0;
                StartBehavior = StartBehavior.WaitForBarClose;
                TimeInForce = TimeInForce.Day;
                TraceOrders = true;
                RealtimeErrorHandling = RealtimeErrorHandling.StopCancelCloseStrategy;
                StopTargetHandling = StopTargetHandling.PerEntryExecution;
                BarsRequiredToTrade = 1;
                IsInstantiatedOnEachOptimizationIteration = true;
            }
            else if (State == State.Configure)
            {
            }
            else if (State == State.DataLoaded)
            {
                // Create logs directory
                string dir = System.IO.Path.GetDirectoryName(logPath);
                if (!System.IO.Directory.Exists(dir))
                    System.IO.Directory.CreateDirectory(dir);

                // Open log file
                logWriter = new System.IO.StreamWriter(logPath, true);
                Log($"OrderRouter started on {DateTime.Now}");

                // Start HTTP listener
                StartHttpListener();
            }
        }

        private void StartHttpListener()
        {
            try
            {
                httpListener = new HttpListener();
                httpListener.Prefixes.Add("http://localhost:8765/");
                httpListener.Start();
                Log("HTTP listener started on localhost:8765");

                // Listen for requests in background
                System.Threading.ThreadPool.QueueUserWorkItem(_ => ListenForSignals());
            }
            catch (Exception e)
            {
                Log($"HTTP listener error: {e.Message}");
            }
        }

        private void ListenForSignals()
        {
            while (httpListener.IsListening)
            {
                try
                {
                    HttpListenerContext context = httpListener.GetContext();
                    HttpListenerRequest request = context.Request;
                    HttpListenerResponse response = context.Response;

                    if (request.HttpMethod == "POST" && request.Url.AbsolutePath == "/signal")
                    {
                        // Read POST body
                        StreamReader reader = new StreamReader(request.InputStream);
                        string json = reader.ReadToEnd();

                        // Parse JSON (simple parsing)
                        string action = ExtractJsonValue(json, "action");
                        string instrument = ExtractJsonValue(json, "instrument");
                        string quantity = ExtractJsonValue(json, "quantity");

                        Log($"Signal received: {action} {quantity} {instrument}");

                        // Place order
                        if (action == "LONG")
                            EnterLong(Convert.ToInt32(quantity), "Entry");
                        else if (action == "SHORT")
                            EnterShort(Convert.ToInt32(quantity), "Entry");
                        else if (action == "FLAT")
                            ExitLong();

                        // Send response
                        response.StatusCode = 200;
                        byte[] buffer = System.Text.Encoding.UTF8.GetBytes("OK");
                        response.OutputStream.Write(buffer, 0, buffer.Length);
                        response.OutputStream.Close();
                    }
                    else
                    {
                        response.StatusCode = 404;
                        response.OutputStream.Close();
                    }
                }
                catch (Exception e)
                {
                    Log($"HTTP error: {e.Message}");
                }
            }
        }

        private string ExtractJsonValue(string json, string key)
        {
            try
            {
                string search = $"\"{key}\":\"";
                int idx = json.IndexOf(search);
                if (idx == -1)
                {
                    search = $"\"{key}\":";
                    idx = json.IndexOf(search);
                    if (idx == -1) return "";
                    idx += search.Length;
                    int endIdx = json.IndexOf(",", idx);
                    if (endIdx == -1) endIdx = json.IndexOf("}", idx);
                    return json.Substring(idx, endIdx - idx).Trim();
                }
                idx += search.Length;
                int end = json.IndexOf("\"", idx);
                return json.Substring(idx, end - idx);
            }
            catch
            {
                return "";
            }
        }

        protected override void OnBarUpdate()
        {
            // Strategy logic here (if needed)
        }

        protected override void OnExecutionUpdate(Execution execution, string executionId, double price, int quantity, MarketPosition marketPosition, string orderId, DateTime time)
        {
            Log($"Fill: {execution.Order.OrderAction} {execution.Quantity} @ {execution.Price}");
        }

        private void Log(string message)
        {
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff");
            string logLine = $"[{timestamp}] {message}";
            
            if (logWriter != null)
            {
                logWriter.WriteLine(logLine);
                logWriter.Flush();
            }
            
            Print(logLine);
        }

        protected override void OnTermination()
        {
            if (httpListener != null && httpListener.IsListening)
            {
                httpListener.Stop();
                httpListener.Close();
            }
            if (logWriter != null)
            {
                logWriter.Close();
                logWriter.Dispose();
            }
        }
    }
}

#region NinjaScript generated code. Neither change nor remove.

namespace Ninjatrader.NinjaScript.Strategies
{
    public partial class Strategy : Ninjatrader.Cbi.Strategy
    {
    }
}

#endregion