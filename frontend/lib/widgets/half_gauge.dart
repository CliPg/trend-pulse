/*
Half-circle gauge widget for displaying metrics with progress and gradient.
Used for both sentiment score and trend heat indicators.
*/
import "package:flutter/material.dart";
import "dart:math" as math;

class HalfGauge extends StatelessWidget {
  final double value;
  final double maxValue;
  final String title;
  final String subtitle;
  final List<Color> gradientColors;
  final IconData? icon;
  final String? emoji;

  const HalfGauge({
    super.key,
    required this.value,
    required this.maxValue,
    required this.title,
    required this.subtitle,
    required this.gradientColors,
    this.icon,
    this.emoji,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = (value / maxValue).clamp(0.0, 1.0);
    final primaryColor = gradientColors.first;

    return Container(
      height: 240,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            gradientColors[0].withOpacity(0.08),
            gradientColors.length > 1
                ? gradientColors[1].withOpacity(0.05)
                : gradientColors[0].withOpacity(0.03),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 5),
          ),
        ],
        border: Border.all(
          color: primaryColor.withOpacity(0.2),
          width: 1.5,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Title
            Text(
              title,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
              ),
            ),
            // Half-circle gauge
            Expanded(
              child: SizedBox(
                width: double.infinity,
                child: CustomPaint(
                  painter: _HalfGaugePainter(
                    percentage: percentage,
                    gradientColors: gradientColors,
                  ),
                ),
              ),
            ),
            // Value and subtitle
            Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (emoji != null) ...[
                  Text(
                    emoji!,
                    style: const TextStyle(fontSize: 32),
                  ),
                  const SizedBox(height: 2),
                ],
                Text(
                  value.toStringAsFixed(0),
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    foreground: Paint()
                      ..shader = LinearGradient(
                        colors: gradientColors,
                      ).createShader(
                        const Rect.fromLTWH(0.0, 0.0, 200.0, 70.0),
                      ),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle.toUpperCase(),
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: primaryColor,
                    letterSpacing: 1.0,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            // Progress bar with gradient
            Container(
              height: 6,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
              ),
              child: Stack(
                children: [
                  Container(
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: percentage,
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: gradientColors,
                        ),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 4),
            // Percentage text
            Text(
              "${(percentage * 100).toStringAsFixed(0)}%",
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HalfGaugePainter extends CustomPainter {
  final double percentage;
  final List<Color> gradientColors;

  _HalfGaugePainter({
    required this.percentage,
    required this.gradientColors,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height - 10);
    final radius = math.min(size.width, size.height * 2) / 2 - 20;

    // Background arc
    final backgroundPaint = Paint()
      ..color = Colors.grey[200]!
      ..style = PaintingStyle.stroke
      ..strokeWidth = 18
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      math.pi,
      math.pi,
      false,
      backgroundPaint,
    );

    // Progress arc with gradient
    final progressPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 18
      ..strokeCap = StrokeCap.round
      ..shader = LinearGradient(
        colors: gradientColors,
      ).createShader(
        Rect.fromCircle(center: center, radius: radius),
      );

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      math.pi,
      math.pi * percentage,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(_HalfGaugePainter oldDelegate) {
    return oldDelegate.percentage != percentage ||
        oldDelegate.gradientColors != gradientColors;
  }
}
