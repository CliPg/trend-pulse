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
        builder: (context, setDialogState) {
          final colorScheme = Theme.of(context).colorScheme;

          return AlertDialog(
            title: const Text("Create Subscription"),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Keyword input
                  Row(
                    children: [
                      Icon(Icons.search, size: 20, color: Colors.grey[700]),
                      const SizedBox(width: 8),
                      const Text(
                        "Keyword",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: keywordController,
                    decoration: InputDecoration(
                      hintText: "e.g., iPhone 16 Pro",
                      filled: true,
                      fillColor: Colors.grey[50],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide.none,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: colorScheme.primary, width: 2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Platforms
                  Row(
                    children: [
                      Icon(Icons.dashboard, size: 20, color: Colors.grey[700]),
                      const SizedBox(width: 8),
                      const Text(
                        "Platforms",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                      const Spacer(),
                      Text(
                        "${selectedPlatforms.length} selected",
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
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
                  const SizedBox(height: 20),

                  // Alert Threshold
                  Row(
                    children: [
                      Icon(Icons.warning_amber_rounded, size: 20, color: Colors.grey[700]),
                      const SizedBox(width: 8),
                      const Text(
                        "Alert Threshold",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: thresholdController,
                    decoration: InputDecoration(
                      hintText: "Trigger alert if sentiment below this value",
                      filled: true,
                      fillColor: Colors.grey[50],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide.none,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: colorScheme.primary, width: 2),
                      ),
                      suffixIcon: Container(
                        margin: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.orange.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.warning, color: Colors.orange.shade700, size: 20),
                      ),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                  const SizedBox(height: 20),

                  // Check Interval
                  Row(
                    children: [
                      Icon(Icons.schedule, size: 20, color: Colors.grey[700]),
                      const SizedBox(width: 8),
                      const Text(
                        "Check Interval (hours)",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: intervalController,
                    decoration: InputDecoration(
                      hintText: "How often to check this keyword",
                      filled: true,
                      fillColor: Colors.grey[50],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide.none,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: colorScheme.primary, width: 2),
                      ),
                      suffixIcon: Container(
                        margin: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.access_time, color: Colors.blue.shade700, size: 20),
                      ),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                  const SizedBox(height: 20),

                  // Posts Limit
                  Row(
                    children: [
                      Icon(Icons.article, size: 20, color: Colors.grey[700]),
                      const SizedBox(width: 8),
                      const Text(
                        "Posts per Platform",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: limitController,
                    decoration: InputDecoration(
                      hintText: "Number of posts to collect each time",
                      filled: true,
                      fillColor: Colors.grey[50],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide.none,
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(15),
                        borderSide: BorderSide(color: colorScheme.primary, width: 2),
                      ),
                      suffixIcon: Container(
                        margin: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.green.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(Icons.format_list_numbered, color: Colors.green.shade700, size: 20),
                      ),
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
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
                child: const Text("Subscribe"),
              ),
            ],
          );
        },
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
    final colorScheme = Theme.of(context).colorScheme;

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: const Color(0xFFF8F9FA),
        appBar: AppBar(
          title: const Text(
            "Subscription Manager",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.white,
              fontSize: 22,
            ),
          ),
          backgroundColor: colorScheme.primary,
          flexibleSpace: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  colorScheme.primary,
                  colorScheme.secondary,
                ],
              ),
            ),
          ),
          bottom: TabBar(
            labelColor: Colors.white70,
            unselectedLabelColor: Colors.white54,
            indicatorColor: Colors.white,
            tabs: const [
              Tab(text: "My Subscriptions", icon: Icon(Icons.notifications_active)),
              Tab(text: "Alert History", icon: Icon(Icons.history)),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white),
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
          backgroundColor: Theme.of(context).colorScheme.primary,
          child: const Icon(Icons.add, color: Colors.white),
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
            const Text(
              "No Subscriptions",
              style: TextStyle(fontSize: 18, color: Colors.grey, fontWeight: FontWeight.w500),
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
        padding: const EdgeInsets.all(20),
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

  Map<String, dynamic> _getPlatformInfo(String platform) {
    switch (platform) {
      case "reddit":
        return {
          "label": "Reddit",
          "icon": Icons.reddit,
          "color": const Color(0xFFFF4500),
        };
      case "youtube":
        return {
          "label": "YouTube",
          "icon": Icons.play_circle_filled,
          "color": const Color(0xFFFF0000),
        };
      case "twitter":
        return {
          "label": "X (Twitter)",
          "icon": Icons.alternate_email,
          "color": const Color(0xFF000000),
        };
      default:
        return {
          "label": platform,
          "icon": Icons.public,
          "color": Colors.grey,
        };
    }
  }

  @override
  Widget build(BuildContext context) {
    final platforms = subscription.platforms?.split(",") ?? [];
    final colorScheme = Theme.of(context).colorScheme;

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
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with keyword and delete button
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.search,
                    color: colorScheme.primary,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        subscription.keyword,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          Icon(Icons.schedule, size: 14, color: Colors.grey[600]),
                          const SizedBox(width: 4),
                          Text(
                            "Check every ${subscription.intervalHours}h",
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
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: Colors.red),
                  onPressed: onDelete,
                  tooltip: "Unsubscribe",
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Platforms
            Row(
              children: [
                Icon(Icons.dashboard, size: 18, color: Colors.grey[700]),
                const SizedBox(width: 8),
                Text(
                  "Platforms:",
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Wrap(
                    spacing: 6,
                    children: platforms.map((platform) {
                      final platformInfo = _getPlatformInfo(platform);
                      return Chip(
                        label: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              platformInfo["icon"] as IconData,
                              size: 14,
                              color: platformInfo["color"] as Color,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              platformInfo["label"] as String,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: Colors.grey[700],
                              ),
                            ),
                          ],
                        ),
                        padding: EdgeInsets.zero,
                        labelPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        backgroundColor: (platformInfo["color"] as Color).withOpacity(0.1),
                        side: BorderSide(
                          color: (platformInfo["color"] as Color).withOpacity(0.3),
                          width: 1,
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Stats
            Row(
              children: [
                Expanded(
                  child: _StatItem(
                    icon: Icons.warning_amber_rounded,
                    label: "Threshold",
                    value: subscription.alertThreshold.toString(),
                    color: Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _StatItem(
                    icon: Icons.format_list_numbered,
                    label: "Limit",
                    value: subscription.postLimit.toString(),
                    color: Colors.green,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _StatItem(
                    icon: Icons.access_time,
                    label: "Last Check",
                    value: _formatDate(subscription.lastCheckedAt),
                    color: Colors.blue,
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

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 16, color: color),
              const SizedBox(width: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
