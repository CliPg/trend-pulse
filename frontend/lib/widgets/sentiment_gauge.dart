/*
Sentiment gauge widget with modern design.
Features circular progress with gradient colors and smooth animations.
*/
import "package:flutter/material.dart";
import "package:fl_chart/fl_chart.dart";

class SentimentGauge extends StatelessWidget {
  final double sentimentScore;
  final String sentimentLabel;

  const SentimentGauge({
    super.key,
    required this.sentimentScore,
    required this.sentimentLabel,
  });

  Color _getColor(double score) {
    if (score >= 70) return const Color(0xFF4CAF50);
    if (score >= 40) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }

  String _getEmoji(double score) {
    if (score >= 80) return "😄";
    if (score >= 60) return "🙂";
    if (score >= 40) return "😐";
    if (score >= 20) return "😟";
    return "😢";
  }

  @override
  Widget build(BuildContext context) {
    final color = _getColor(sentimentScore);
    final emoji = _getEmoji(sentimentScore);

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            "Sentiment Score",
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 24),
          Stack(
            alignment: Alignment.center,
            children: [
              // Background circle
              SizedBox(
                height: 180,
                width: 180,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 0,
                    centerSpaceRadius: 70,
                    sections: [
                      PieChartSectionData(
                        value: 100,
                        color: Colors.grey[100],
                        radius: 40,
                        showTitle: false,
                      ),
                    ],
                  ),
                ),
              ),
              // Progress circle
              SizedBox(
                height: 180,
                width: 180,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 0,
                    centerSpaceRadius: 70,
                    sections: [
                      PieChartSectionData(
                        value: sentimentScore,
                        color: color,
                        radius: 40,
                        showTitle: false,
                      ),
                    ],
                  ),
                ),
              ),
              // Center content
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    emoji,
                    style: const TextStyle(fontSize: 40),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    sentimentScore.toStringAsFixed(0),
                    style: TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  Text(
                    sentimentLabel.toUpperCase(),
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: color,
                      letterSpacing: 1.2,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildLegendItem("Negative", 0, 40, const Color(0xFFF44336)),
              _buildLegendItem("Neutral", 40, 70, const Color(0xFFFF9800)),
              _buildLegendItem("Positive", 70, 100, const Color(0xFF4CAF50)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, double start, double end, Color color) {
    final isSelected = sentimentScore >= start && sentimentScore < end;
    return Column(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: color.withOpacity(0.5),
                      blurRadius: 8,
                      spreadRadius: 2,
                    ),
                  ]
                : null,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            color: isSelected ? color : Colors.grey[600],
          ),
        ),
      ],
    );
  }
}
