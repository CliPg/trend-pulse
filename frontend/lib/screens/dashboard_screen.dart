/*
Main dashboard screen for TrendPulse.
Modern UI with gradient backgrounds, cards, and smooth animations.
*/
import "package:flutter/material.dart";
import "package:flutter/services.dart";
import "package:flutter/foundation.dart" show kIsWeb;
import "../services/api_service.dart";
import "../services/mock_data.dart";
import "../widgets/half_gauge.dart";
import "../widgets/opinion_card.dart";
import "../widgets/post_list.dart";
import "subscriptions_screen.dart";

// Conditional import for web platform - default to stub, use web viewer only when dart:html is available
import "../widgets/mindmap_stub.dart" if (dart.library.html) "../widgets/mindmap_viewer.dart";

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _keywordController = TextEditingController();
  bool _isLoading = false;
  AnalysisResult? _result;
  String? _errorMessage;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // Platform selection
  final List<String> _availablePlatforms = ["reddit", "youtube", "twitter"];
  final Set<String> _selectedPlatforms = {"reddit", "youtube"};

  // Language and limit settings
  String _selectedLanguage = "en";
  final TextEditingController _limitController = TextEditingController(text: "50");

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _keywordController.dispose();
    _limitController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _analyzeKeyword() async {
    if (_keywordController.text.isEmpty) return;

    if (_selectedPlatforms.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text("Please select at least one platform"),
          backgroundColor: Colors.orange.shade600,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
      return;
    }

    // Validate limit input
    final limitText = _limitController.text;
    final limit = int.tryParse(limitText);
    if (limit == null || limit <= 0 || limit > 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text("Please enter a valid limit (1-200)"),
          backgroundColor: Colors.orange.shade600,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _result = null;
      _errorMessage = null;
    });

    try {
      final result = await ApiService().analyzeKeyword(
        keyword: _keywordController.text,
        language: _selectedLanguage,
        platforms: _selectedPlatforms.toList(),
        limitPerPlatform: limit,
      );

      setState(() {
        _result = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString();
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Error: $_errorMessage"),
            backgroundColor: Colors.red.shade400,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        );
      }
    }
  }

  void _showMockDataOptions() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Load Test Data"),
        content: const Text("Select which mock data scenario to load:"),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _loadSpecificMockData("positive");
            },
            child: const Text("Positive Sentiment"),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _loadSpecificMockData("negative");
            },
            child: const Text("Negative Sentiment", style: TextStyle(color: Colors.red)),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _loadSpecificMockData("neutral");
            },
            child: const Text("Neutral Sentiment"),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Cancel"),
          ),
        ],
      ),
    );
  }

  void _loadSpecificMockData(String type) {
    setState(() {
      _isLoading = true;
      _result = null;
    });

    Future.delayed(const Duration(milliseconds: 500), () {
      AnalysisResult mockResult;
      switch (type) {
        case "negative":
          mockResult = MockData.getMockNegativeResult();
          break;
        case "neutral":
          mockResult = MockData.getMockNeutralResult();
          break;
        default:
          mockResult = MockData.getMockAnalysisResult();
      }

      setState(() {
        _result = mockResult;
        _isLoading = false;
        _keywordController.text = _result!.keyword;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Test data loaded: $type sentiment"),
            backgroundColor: Colors.green.shade600,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              colorScheme.primary.withOpacity(0.05),
              colorScheme.secondary.withOpacity(0.05),
            ],
          ),
        ),
        child: SafeArea(
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverAppBar(
                expandedHeight: 120,
                floating: false,
                pinned: true,
                backgroundColor: colorScheme.primary,
                actions: [
                  // Test Data button
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: _showMockDataOptions,
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.orange.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: Colors.orange.withOpacity(0.5),
                              width: 1.5,
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.science,
                                color: Colors.white,
                                size: 16,
                              ),
                              const SizedBox(width: 6),
                              Text(
                                "Test Data",
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  // Subscriptions button
                  Padding(
                    padding: const EdgeInsets.only(right: 16),
                    child: Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const SubscriptionsScreen(),
                            ),
                          );
                        },
                        borderRadius: BorderRadius.circular(20),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: Colors.white.withOpacity(0.5),
                              width: 1.5,
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(
                                Icons.notifications_active_outlined,
                                color: Colors.white,
                                size: 16,
                              ),
                              const SizedBox(width: 6),
                              Text(
                                "Subscriptions",
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
                flexibleSpace: FlexibleSpaceBar(
                  title: const Text(
                    "TrendPulse",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                      fontSize: 28,
                    ),
                  ),
                  background: Container(
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
                ),
              ),

              // Main Content
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Search Input
                      _buildSearchCard(colorScheme),

                      const SizedBox(height: 24),

                      // Loading Indicator
                      if (_isLoading) _buildLoadingIndicator(),

                      // Results
                      if (_result != null) ...[
                        _buildResults(colorScheme),
                      ],

                      // Initial State
                      if (!_isLoading && _result == null) ...[
                        _buildInitialState(),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSearchCard(ColorScheme colorScheme) {
    return Container(
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
            Row(
              children: [
                Text(
                  "Analyze Sentiment",
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: colorScheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              "Enter a keyword to discover what people are saying across social media",
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _keywordController,
              decoration: InputDecoration(
                hintText: "Try: iPhone, Python, DeepSeek...",
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
                    color: colorScheme.primary,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.search, color: Colors.white),
                    onPressed: _isLoading ? null : _analyzeKeyword,
                  ),
                ),
              ),
              onSubmitted: (_) => _analyzeKeyword(),
            ),
            const SizedBox(height: 20),

            // Platform Selection
            _buildPlatformSelector(colorScheme),

            const SizedBox(height: 20),

            // Language and Limit Settings
            _buildSettingsRow(colorScheme),
          ],
        ),
      ),
    );
  }

  Widget _buildPlatformSelector(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(
              Icons.dashboard,
              size: 20,
              color: Colors.grey[700],
            ),
            const SizedBox(width: 8),
            Text(
              "Select Platforms",
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.grey[800],
              ),
            ),
            const Spacer(),
            Text(
              "${_selectedPlatforms.length} selected",
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
          spacing: 10,
          runSpacing: 10,
          children: _availablePlatforms.map((platform) {
            final isSelected = _selectedPlatforms.contains(platform);
            final platformInfo = _getPlatformInfo(platform);

            return FilterChip(
              selected: isSelected,
              label: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    platformInfo["icon"] as IconData,
                    size: 18,
                    color: isSelected ? Colors.white : platformInfo["color"] as Color,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    platformInfo["label"] as String,
                    style: TextStyle(
                      color: isSelected ? Colors.white : Colors.grey[700],
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _selectedPlatforms.add(platform);
                  } else {
                    _selectedPlatforms.remove(platform);
                  }
                });
              },
              selectedColor: platformInfo["color"] as Color,
              backgroundColor: Colors.grey[100],
              checkmarkColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(
                  color: isSelected
                      ? (platformInfo["color"] as Color)
                      : Colors.grey[300]!,
                  width: isSelected ? 1.5 : 1,
                ),
              ),
              elevation: isSelected ? 2 : 0,
            );
          }).toList(),
        ),
      ],
    );
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

  Widget _buildSettingsRow(ColorScheme colorScheme) {
    return Row(
      children: [
        // Language Selector
        Expanded(
          child: _buildLanguageSelector(colorScheme),
        ),
        const SizedBox(width: 16),
        // Limit Input
        Expanded(
          child: _buildLimitInput(colorScheme),
        ),
      ],
    );
  }

  Widget _buildLanguageSelector(ColorScheme colorScheme) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Row(
              children: [
                Icon(
                  Icons.language,
                  size: 16,
                  color: Colors.grey[700],
                ),
                const SizedBox(width: 6),
                Text(
                  "Language",
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            child: SegmentedButton<String>(
              segments: const [
                ButtonSegment(
                  value: "en",
                  label: Text("EN", style: TextStyle(fontWeight: FontWeight.w600)),
                  icon: Icon(Icons.abc, size: 18),
                ),
                ButtonSegment(
                  value: "zh",
                  label: Text("中", style: TextStyle(fontWeight: FontWeight.w600)),
                  icon: Icon(Icons.translate, size: 18),
                ),
              ],
              selected: {_selectedLanguage},
              onSelectionChanged: (Set<String> newSelection) {
                setState(() {
                  _selectedLanguage = newSelection.first;
                });
              },
              style: ButtonStyle(
                backgroundColor: MaterialStateProperty.resolveWith((states) {
                  if (states.contains(MaterialState.selected)) {
                    return colorScheme.primary;
                  }
                  return Colors.transparent;
                }),
                foregroundColor: MaterialStateProperty.resolveWith((states) {
                  if (states.contains(MaterialState.selected)) {
                    return Colors.white;
                  }
                  return Colors.grey[700];
                }),
                padding: MaterialStateProperty.all(
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLimitInput(ColorScheme colorScheme) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Row(
              children: [
                Icon(
                  Icons.format_list_numbered,
                  size: 16,
                  color: Colors.grey[700],
                ),
                const SizedBox(width: 6),
                Text(
                  "Posts Limit",
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            child: TextField(
              controller: _limitController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                hintText: "1-200",
                hintStyle: TextStyle(color: Colors.grey[400], fontSize: 13),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
                isDense: true,
              ),
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return Container(
      padding: const EdgeInsets.all(40),
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
          const CircularProgressIndicator(),
          const SizedBox(height: 20),
          Text(
            "Analyzing social media...",
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: Colors.grey[700],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "This may take 30-60 seconds",
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInitialState() {
    return Container(
      padding: const EdgeInsets.all(40),
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
          Icon(
            Icons.search,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 20),
          Text(
            "Start Your Analysis",
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: Colors.grey[800],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Enter a keyword above to discover public sentiment",
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildResults(ColorScheme colorScheme) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Gauges Row - Sentiment and Heat
          Row(
            children: [
              Expanded(
                child: HalfGauge(
                  value: _result!.overallSentiment,
                  maxValue: 100,
                  title: "Sentiment Score",
                  subtitle: _result!.sentimentLabel,
                  gradientColors: _getSentimentGradient(_result!.overallSentiment),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: HalfGauge(
                  value: _calculateHeatScore().toDouble(),
                  maxValue: (_result!.postsCount * 10).toDouble(),
                  title: "Trend Heat",
                  subtitle: "Engagement Level",
                  gradientColors: const [Color(0xFFFF6B35), Color(0xFFFF9472)],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Stats Row
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  "Posts Analyzed",
                  _result!.postsCount.toString(),
                  Icons.article,
                  Colors.blue,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  "Sentiment",
                  _result!.overallSentiment.toStringAsFixed(0),
                  Icons.sentiment_satisfied,
                  _getSentimentColor(_result!.overallSentiment),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildStatCard(
                  "Opinions",
                  _result!.opinionClusters.length.toString(),
                  Icons.psychology,
                  Colors.purple,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Summary Card
          _buildSummaryCard(colorScheme),
          const SizedBox(height: 24),

          // Mind Map (if available)
          if (_result?.mermaid != null && _result!.mermaid!.mindmap.isNotEmpty) ...[
            _buildSectionHeader("Opinion Mind Map", Icons.hub_rounded),
            const SizedBox(height: 12),
            MindMapViewer(
              treeData: _result!.mermaid!.mindmap,
              title: _result!.keyword,
              height: 550,
            ),
            const SizedBox(height: 24),
          ],

          // Opinion Clusters
          _buildSectionHeader("Key Opinions", Icons.lightbulb),
          const SizedBox(height: 12),
          ..._result!.opinionClusters.map((cluster) => OpinionCard(
                cluster: cluster,
              )),
          const SizedBox(height: 24),

          // Source Posts
          _buildSectionHeader("Source Posts", Icons.source),
          const SizedBox(height: 12),
          PostList(posts: _result!.posts),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            colorScheme.primary.withOpacity(0.1),
            colorScheme.secondary.withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: colorScheme.primary.withOpacity(0.2),
          width: 2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: colorScheme.primary,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.summarize, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 12),
              Text(
                "Summary",
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const Spacer(),
              // Copy button
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () {
                    Clipboard.setData(ClipboardData(text: _result!.summary));
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: const Text("Summary copied to clipboard"),
                        backgroundColor: Colors.green.shade600,
                        behavior: SnackBarBehavior.floating,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                  borderRadius: BorderRadius.circular(12),
                  child: Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: colorScheme.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.copy,
                          color: colorScheme.primary,
                          size: 18,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          "Copy",
                          style: TextStyle(
                            color: colorScheme.primary,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            _result!.summary,
            style: TextStyle(
              fontSize: 15,
              height: 1.6,
              color: Colors.grey[800],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primary,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: Colors.white, size: 20),
        ),
        const SizedBox(width: 12),
        Text(
          title,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }

  Color _getSentimentColor(double score) {
    if (score >= 70) return Colors.green;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }

  List<Color> _getSentimentGradient(double score) {
    if (score >= 70) {
      return [const Color(0xFF4CAF50), const Color(0xFF81C784)];
    }
    if (score >= 40) {
      return [const Color(0xFFFF9800), const Color(0xFFFFB74D)];
    }
    return [const Color(0xFFF44336), const Color(0xFFEF5350)];
  }

  String _getSentimentEmoji(double score) {
    if (score >= 80) return "😄";
    if (score >= 60) return "🙂";
    if (score >= 40) return "😐";
    if (score >= 20) return "😟";
    return "😢";
  }

  int _calculateHeatScore() {
    // Calculate heat score based on posts and engagement
    int totalEngagement = 0;
    for (var post in _result!.posts) {
      totalEngagement += (post.upvotes ?? 0) + (post.likes ?? 0);
    }
    // Heat score = posts count + average engagement
    return _result!.postsCount + (totalEngagement / _result!.postsCount).round();
  }
}
