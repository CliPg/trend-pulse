/*
Subscription Management Screen
Allows users to create, view, and cancel keyword monitoring subscriptions.
*/
import "package:flutter/material.dart";
import "../services/api_service.dart";
import "../widgets/alert_history_widget.dart";

class SubscriptionsScreen extends StatefulWidget {
  const SubscriptionsScreen({super.key});

  @override
  State<SubscriptionsScreen> createState() => _SubscriptionsScreenState();
}

class _SubscriptionsScreenState extends State<SubscriptionsScreen> {
  final ApiService _apiService = ApiService();
  List<Subscription> _subscriptions = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadSubscriptions();
  }

  Future<void> _loadSubscriptions() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final subscriptions = await _apiService.getSubscriptions();
      setState(() {
        _subscriptions = subscriptions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _showCreateSubscriptionDialog() async {
    final keywordController = TextEditingController();
    final thresholdController = TextEditingController(text: "30.0");
    final intervalController = TextEditingController(text: "6");
    final limitController = TextEditingController(text: "50");

    final platforms = ["reddit", "youtube", "twitter"];
    final selectedPlatforms = <String>{"reddit", "youtube"};
    final selectedLanguage = "en";

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text("Create Subscription"),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: keywordController,
                  decoration: const InputDecoration(
                    labelText: "Keyword",
                    hintText: "e.g., iPhone 16 Pro",
                  ),
                ),
                const SizedBox(height: 16),
                const Text("Platforms:", style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: platforms.map((platform) {
                    final isSelected = selectedPlatforms.contains(platform);
                    return FilterChip(
                      label: Text(platform.toUpperCase()),
                      selected: isSelected,
                      onSelected: (selected) {
                        setDialogState(() {
                          if (selected) {
                            selectedPlatforms.add(platform);
                          } else {
                            selectedPlatforms.remove(platform);
                          }
                        });
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: thresholdController,
                  decoration: const InputDecoration(
                    labelText: "Alert Threshold (0-100)",
                    hintText: "Trigger alert if sentiment below this value",
                  ),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: intervalController,
                  decoration: const InputDecoration(
                    labelText: "Check Interval (hours)",
                    hintText: "How often to check this keyword",
                  ),
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: limitController,
                  decoration: const InputDecoration(
                    labelText: "Posts per Platform",
                    hintText: "Number of posts to collect each time",
                  ),
                  keyboardType: TextInputType.number,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () async {
                final keyword = keywordController.text.trim();
                if (keyword.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text("Please enter a keyword")),
                  );
                  return;
                }

                try {
                  final threshold = double.parse(thresholdController.text);
                  final interval = int.parse(intervalController.text);
                  final limit = int.parse(limitController.text);

                  await _apiService.createSubscription(
                    keyword: keyword,
                    platforms: selectedPlatforms.toList(),
                    language: selectedLanguage,
                    postLimit: limit,
                    alertThreshold: threshold,
                    intervalHours: interval,
                  );

                  Navigator.pop(context);
                  await _loadSubscriptions();

                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text("Subscribed to: $keyword")),
                    );
                  }
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text("Subscription failed: $e")),
                    );
                  }
                }
              },
              child: const Text("Subscribe"),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteSubscription(Subscription subscription) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Cancel Subscription"),
        content: Text("Are you sure you want to unsubscribe from \"${subscription.keyword}\"?"),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text("Cancel"),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text("Confirm"),
          ),
        ],
      ),
    );

    if (confirm == true) {
      try {
        await _apiService.deleteSubscription(subscription.id);
        await _loadSubscriptions();

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text("Unsubscribed from: ${subscription.keyword}")),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text("Failed to unsubscribe: $e")),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text("Subscription Manager"),
          bottom: const TabBar(
            tabs: [
              Tab(text: "My Subscriptions", icon: Icon(Icons.notifications_active)),
              Tab(text: "Alert History", icon: Icon(Icons.history)),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loadSubscriptions,
              tooltip: "Refresh",
            ),
          ],
        ),
        body: TabBarView(
          children: [
            _buildSubscriptionsTab(),
            const AlertHistoryWidget(),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _showCreateSubscriptionDialog,
          tooltip: "Create Subscription",
          child: const Icon(Icons.add),
        ),
      ),
    );
  }

  Widget _buildSubscriptionsTab() {
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
              onPressed: _loadSubscriptions,
              child: const Text("Retry"),
            ),
          ],
        ),
      );
    }

    if (_subscriptions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.notifications_off, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              "No Subscriptions",
              style: TextStyle(fontSize: 18, color: Colors.grey[600]),
            ),
            const SizedBox(height: 8),
            Text(
              "Tap the + button to create a subscription",
              style: TextStyle(color: Colors.grey[500]),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadSubscriptions,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _subscriptions.length,
        itemBuilder: (context, index) {
          final subscription = _subscriptions[index];
          return _SubscriptionCard(
            subscription: subscription,
            onDelete: () => _deleteSubscription(subscription),
          );
        },
      ),
    );
  }
}

class _SubscriptionCard extends StatelessWidget {
  final Subscription subscription;
  final VoidCallback onDelete;

  const _SubscriptionCard({
    required this.subscription,
    required this.onDelete,
  });

  String _formatDate(String? dateStr) {
    if (dateStr == null) return "Not checked";
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final diff = now.difference(date);

      if (diff.inMinutes < 60) {
        return "${diff.inMinutes}m ago";
      } else if (diff.inHours < 24) {
        return "${diff.inHours}h ago";
      } else {
        return "${diff.inDays}d ago";
      }
    } catch (e) {
      return "Unknown";
    }
  }

  @override
  Widget build(BuildContext context) {
    final platforms = subscription.platforms?.split(",") ?? [];

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.search, color: Colors.blue),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        subscription.keyword,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(Icons.schedule, size: 14, color: Colors.grey[600]),
                          const SizedBox(width: 4),
                          Text(
                            "Check every ${subscription.intervalHours}h",
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: Colors.red),
                  onPressed: onDelete,
                  tooltip: "Unsubscribe",
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 6,
              children: platforms.map((platform) {
                return Chip(
                  label: Text(
                    platform.toUpperCase(),
                    style: const TextStyle(fontSize: 10),
                  ),
                  padding: EdgeInsets.zero,
                  labelPadding: const EdgeInsets.symmetric(horizontal: 6),
                  backgroundColor: Colors.purple.withOpacity(0.1),
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _InfoChip(
                  icon: Icons.warning_amber_rounded,
                  label: "Threshold",
                  value: subscription.alertThreshold.toString(),
                  color: Colors.orange,
                ),
                const SizedBox(width: 8),
                _InfoChip(
                  icon: Icons.article,
                  label: "Limit",
                  value: subscription.postLimit.toString(),
                  color: Colors.green,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _InfoChip(
                    icon: Icons.access_time,
                    label: "Last Check",
                    value: _formatDate(subscription.lastCheckedAt),
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            "$label: $value",
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
