/*
Opinion card widget with modern card design.
Displays opinion clusters with icons, colors, and smooth styling.
*/
import "package:flutter/material.dart";
import "../services/api_service.dart";

class OpinionCard extends StatelessWidget {
  final OpinionCluster cluster;

  const OpinionCard({super.key, required this.cluster});

  Color _getCardColor(int index) {
    final colors = [
      const Color(0xFF2196F3), // Blue
      const Color(0xFF9C27B0), // Purple
      const Color(0xFFFF9800), // Orange
      const Color(0xFF4CAF50), // Green
      const Color(0xFFE91E63), // Pink
    ];
    return colors[index % colors.length];
  }

  IconData _getIcon(int index) {
    final icons = [
      Icons.lightbulb_outline,
      Icons.chat_bubble_outline,
      Icons.star_outline,
      Icons.favorite_border,
      Icons.bookmark_border,
    ];
    return icons[index % icons.length];
  }

  @override
  Widget build(BuildContext context) {
    // Use hash code to get consistent color for same cluster
    final colorIndex = cluster.label.hashCode.abs();
    final color = _getCardColor(colorIndex);
    final icon = _getIcon(colorIndex);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: color, size: 26),
            ),
            const SizedBox(width: 16),
            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title and badge
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          cluster.label,
                          style: const TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: color.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.bar_chart,
                              size: 14,
                              color: color.withOpacity(0.8),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              "${cluster.mentionCount}",
                              style: TextStyle(
                                color: color,
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  // Summary
                  Text(
                    cluster.summary,
                    style: TextStyle(
                      fontSize: 14,
                      height: 1.5,
                      color: Colors.grey[700],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
