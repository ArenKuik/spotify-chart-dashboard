// Shared Chart.js look for every chart on the site. Load after chart.js.
Chart.defaults.font.family = '"DM Sans", system-ui, sans-serif';
Chart.defaults.color = "#66746a";          // axis labels and legend text
Chart.defaults.borderColor = "#e9ece4";    // soft grid lines
Chart.defaults.plugins.tooltip.backgroundColor = "#2c3a30";
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.legend.labels.padding = 16;

// Fixed colours for chart lines, checked for colour-blind readers.
// Green and blue are kept apart from orange because those pairs look alike to some readers.
const CHART_COLORS = ["#3f8a5c", "#4f7fc9", "#d9724a", "#a160b0", "#d19b1f"];
