using OxyPlot;
using OxyPlot.Series;
using OxyPlot.Axes;
using System.Timers;
using OxyPlot.WindowsForms;
using EAProject;

public abstract class BaseFigureHandler
{
    protected int size;
    protected double[] x;
    protected LineSeries lineSeries;
    protected PlotModel[] frequencyPlotModels;
    protected LineSeries[] frequencyLineSeries;
    protected int width = 1000;
    protected int height = 600;
    protected bool frequencyPlotFlag = false;
    private PlotView[] frequencyPlotViews;
    private PlotView plotView;
    private PlotModel plotModel;
    private double sampleInterval;
    private Form form;
    private TableLayoutPanel tableLayoutPanel;
    private double[] data;
    private System.Timers.Timer timer;

    public BaseFigureHandler(double sampleinterval = 0.1, double timewindow = 10.0, int size = 4096, string unit = "Pa")
    {
        this.sampleInterval = sampleinterval;
        this.size = size;
        this.x = Enumerable.Range(0, size).Select(i => i * timewindow / size).ToArray();
        this.data = new double[size];

        // Setup initial OxyPlot for the time signal
        this.plotModel = new PlotModel { Title = "Time signal" };
        this.plotModel.Axes.Add(new LinearAxis { Position = AxisPosition.Bottom, Title = "Time (s)", Minimum = 0, Maximum = timewindow });
        this.plotModel.Axes.Add(new LinearAxis { Position = AxisPosition.Left, Title = $"Amplitude ({unit})", Minimum = -30, Maximum = 30});
        this.lineSeries = new LineSeries { Title = null, Color = OxyColors.Blue };
        this.plotModel.Series.Add(this.lineSeries);
        this.plotView = new PlotView { Model = this.plotModel, Dock = DockStyle.Fill };

        for (int j = 0; j < this.size; j++)
        {
            this.lineSeries.Points.Add(new DataPoint(this.x[j], this.data[j]));
        }

        // Setup Timer
        this.timer = new System.Timers.Timer(this.sampleInterval * 1000);
        this.timer.Elapsed += OnTimedEvent;
        this.timer.Start();
    }

    private void OnTimedEvent(Object source, ElapsedEventArgs e)
    {
        if (this.frequencyPlotFlag)
        {
            foreach (var plotView in this.frequencyPlotViews)
            {
                plotView.InvalidatePlot(true);
            }
        }
        else
        {
            this.plotView.InvalidatePlot(true);
        }
        Update();
    }

    protected void FrequencyWindow()
    {
        int numberOfPlots = 0;
        for (int i = 0; i < Handlers.channelInfo.GetLength(0); i++)
        {
            if (Handlers.channelInfo[i,0] == null)
            {
                numberOfPlots = i;
                break;
            }
        }
        this.frequencyPlotFlag = true;
        this.frequencyPlotViews = new PlotView[numberOfPlots];
        this.frequencyPlotModels = new PlotModel[numberOfPlots];
        this.frequencyLineSeries = new LineSeries[numberOfPlots];

        for (int i = 0; i < numberOfPlots; i++)
        {
            var logarithmicAxis = new LogarithmicAxis
            {
                Position = AxisPosition.Bottom,
                Title = "Frequency (Hz)",
                Minimum = 20,
                Maximum = 20000,
                MajorGridlineStyle = LineStyle.Solid,
                MinorGridlineStyle = LineStyle.Dot,
            };  

            this.frequencyPlotModels[i] = new PlotModel { Title = $"Frequency plot {i + 1}" };
            this.frequencyPlotModels[i].Axes.Add(logarithmicAxis);
            this.frequencyPlotModels[i].Axes.Add(new LinearAxis { Position = AxisPosition.Left, Title = "Amplitude (dB)", MajorGridlineStyle = LineStyle.Solid, MinorGridlineStyle = LineStyle.Dot});
            this.frequencyLineSeries[i] = new LineSeries { Title = null, Color = OxyColors.Blue };
            this.frequencyPlotModels[i].Series.Add(this.frequencyLineSeries[i]);
            this.frequencyPlotViews[i] = new PlotView { Model = this.frequencyPlotModels[i], Dock = DockStyle.Fill };
        }

        this.form?.Invoke((Action)(() =>
            {
                this.form.Controls.Clear();

                this.tableLayoutPanel = new TableLayoutPanel
                {
                    RowCount = numberOfPlots,
                    ColumnCount = 1,
                    Dock = DockStyle.Fill,
                    AutoSize = true,
                    AutoScroll = true,
                };

                for (int i = 0; i < numberOfPlots; i++)
                {
                    this.tableLayoutPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100f / numberOfPlots));
                    this.tableLayoutPanel.Controls.Add(this.frequencyPlotViews[i], 0, i);
                }
                this.form.Controls.Add(this.tableLayoutPanel);
                this.form.Invalidate();
                this.form.Update();
            }));
    }

    protected abstract void Update();

    public void Run()
    {
        this.form = new Form
        {
            Width = this.width,
            Height = this.height
        };

        if (!this.frequencyPlotFlag)
        {
            this.form.Controls.Add(this.plotView);
            this.form.Load += (sender, e) => this.plotView.InvalidatePlot(true);
        }
        else
        {
            foreach (var plotview in this.frequencyPlotViews)
            {
                this.form.Controls.Add(plotview);
                this.form.Load += (sender, e) => plotview.InvalidatePlot(true);
            }
        }

        Application.Run(this.form);
    }
}
