/*
Alert History Widget
Displays list of sentiment alerts and allows acknowledgment.
*/
import "package:flutter/material.dart";
import "../services/api_service.dart";

class AlertHistoryWidget extends StatefulWidget {
  const AlertHistoryWidget({super.key});

  @override
  State<AlertHistoryWidget> createState() => _AlertHistoryWidgetState();
}

class _AlertHistoryWidgetState extends State<AlertHistoryWidget> {
  final ApiService _apiService = ApiService();
  List<Alert> _alerts = [];
  bool _isLoading = true;
  String? _error;
  bool? _showAcknowledged;

  @override
  void initState() {
    super.initState();
    _loadAlerts();
  }

  Future<void> _loadAlerts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final alerts = await _apiService.getAlerts(
        limit: 50,
        acknowledged: _showAcknowledged,
      );
      setState(() {
        _alerts = alerts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _acknowledgeAlert(Alert alert) async {
    try {
      await _apiService.acknowledgeAlert(alert.id);
      await _loadAlerts();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("Alert acknowledged")),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Failed to acknowledge: $e")),
        );
      }
    }
  }

  Color _getSentimentColor(double score) {
    if (score < 30) return Colors.red;
    if (score < 50) return Colors.orange;
    if (score < 70) return Colors.yellow;
    return Colors.green;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Filter bar
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          color: Colors.white,
          child: Row(
            children: [
              Icon(Icons.filter_list, size: 20, color: Colors.grey[700]),
              const SizedBox(width: 8),
              const Text("Filter:", style: TextStyle(fontWeight: FontWeight.w600, color: Colors.black87)),
              const SizedBox(width: 16),
              FilterChip(
                label: const Text("All"),
                selected: _showAcknowledged == null,
                onSelected: (selected) {
                  setState(() {
                    _showAcknowledged = null;
                  });
                  _loadAlerts();
                },
              ),
              const SizedBox(width: 8),
              FilterChip(
                label: const Text("Unacknowledged"),
                selected: _showAcknowledged == false,
                onSelected: (selected) {
                  setState(() {
                    _showAcknowledged = false;
                  });
                  _loadAlerts();
                },
              ),
              const SizedBox(width: 8),
              FilterChip(
                label: const Text("Acknowledged"),
                selected: _showAcknowledged == true,
                onSelected: (selected) {
                  setState(() {
                    _showAcknowledged = true;
                  });
                  _loadAlerts();
                },
              ),
            ],
          ),
        ),
        // Alert list
        Expanded(
          child: _buildAlertsList(),
        ),
      ],
    );
  }

  Widget _buildAlertsList() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text("Loading failed: $_error"),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadAlerts,
              child: const Text("Retry"),
            ),
          ],
        ),
      );
    }

    if (_alerts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.check_circle_outline, size: 64, color: Colors.green[200]),
            const SizedBox(height: 16),
            const Text(
              "No Alerts",
              style: TextStyle(fontSize: 18, color: Colors.grey, fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 8),
            Text(
              "Alerts will be triggered when negative sentiment is detected",
              style: TextStyle(color: Colors.grey[500]),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadAlerts,
      child: ListView.builder(
        padding: const EdgeInsets.all(20),
        itemCount: _alerts.length,
        itemBuilder: (context, index) {
          final alert = _alerts[index];
          return _AlertCard(
            alert: alert,
            onAcknowledge: () => _acknowledgeAlert(alert),
            getSentimentColor: _getSentimentColor,
          );
        },
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final Alert alert;
  final VoidCallback onAcknowledge;
  final Color Function(double) getSentimentColor;

  const _AlertCard({
    required this.alert,
    required this.onAcknowledge,
    required this.getSentimentColor,
  });

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final diff = now.difference(date);

      if (diff.inMinutes < 1) {
        return "Just now";
      } else if (diff.inMinutes < 60) {
        return "${diff.inMinutes}m ago";
      } else if (diff.inHours < 24) {
        return "${diff.inHours}h ago";
      } else if (diff.inDays < 7) {
        return "${diff.inDays}d ago";
      } else {
        return "${date.month}/${date.day} ${date.hour}:${date.minute.toString().padLeft(2, '0')}";
      }
    } catch (e) {
      return "Unknown";
    }
  }

  @override
  Widget build(BuildContext context) {
    final sentimentColor = getSentimentColor(alert.sentimentScore);
    final isAcknowledged = alert.acknowledgedAt != null;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
        border: isAcknowledged
            ? null
            : Border.all(color: sentimentColor.withOpacity(0.5), width: 2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: sentimentColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.warning_amber_rounded,
                    color: sentimentColor,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        alert.keyword,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(Icons.access_time, size: 14, color: Colors.grey[600]),
                          const SizedBox(width: 4),
                          Text(
                            _formatDate(alert.createdAt),
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                if (!isAcknowledged)
                  ElevatedButton.icon(
                    onPressed: onAcknowledge,
                    icon: const Icon(Icons.check, size: 18),
                    label: const Text("Acknowledge"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 16),

            // Sentiment Score and Negative Posts
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: sentimentColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _AlertStatItem(
                    icon: Icons.sentiment_dissatisfied,
                    label: "Sentiment",
                    value: "${alert.sentimentScore.toStringAsFixed(1)}/100",
                    color: sentimentColor,
                  ),
                  Container(
                    width: 1,
                    height: 40,
                    color: Colors.grey[300],
                  ),
                  _AlertStatItem(
                    icon: Icons.chat_bubble_outline,
                    label: "Negative Posts",
                    value: "${alert.negativePostsCount}/${alert.postsCount}",
                    color: Colors.orange,
                  ),
                ],
              ),
            ),

            // Summary
            if (alert.summary != null && alert.summary!.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.description, size: 18, color: Colors.grey[700]),
                        const SizedBox(width: 8),
                        const Text(
                          "Summary",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.black87,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      alert.summary!,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.black87,
                        height: 1.5,
                      ),
                      maxLines: 4,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],

            // Acknowledged status
            if (isAcknowledged) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle, size: 16, color: Colors.green.shade700),
                    const SizedBox(width: 6),
                    Text(
                      "Acknowledged ${_formatDate(alert.acknowledgedAt!)}",
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.green.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _AlertStatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _AlertStatItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 24, color: color),
        const SizedBox(height: 6),
        Text(
          value,
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}
