/*
API service for communicating with TrendPulse backend.
Handles HTTP requests and response parsing.
*/
import "dart:convert";
import "package:http/http.dart" as http;

class AnalysisResult {
  final String keyword;
  final int postsCount;
  final double overallSentiment;
  final String sentimentLabel;
  final String summary;
  final List<OpinionCluster> opinionClusters;
  final List<Post> posts;
  final MermaidCharts? mermaid;

  AnalysisResult({
    required this.keyword,
    required this.postsCount,
    required this.overallSentiment,
    required this.sentimentLabel,
    required this.summary,
    required this.opinionClusters,
    required this.posts,
    this.mermaid,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      keyword: json["keyword"],
      postsCount: json["posts_count"],
      overallSentiment: json["overall_sentiment"].toDouble(),
      sentimentLabel: json["sentiment_label"],
      summary: json["summary"],
      opinionClusters: (json["opinion_clusters"] as List)
          .map((e) => OpinionCluster.fromJson(e))
          .toList(),
      posts: (json["posts"] as List).map((e) => Post.fromJson(e)).toList(),
      mermaid: json["mermaid"] != null ? MermaidCharts.fromJson(json["mermaid"]) : null,
    );
  }
}

class MermaidCharts {
  final String mindmap;
  final String pieChart;
  final String flowchart;

  MermaidCharts({
    required this.mindmap,
    required this.pieChart,
    required this.flowchart,
  });

  factory MermaidCharts.fromJson(Map<String, dynamic> json) {
    return MermaidCharts(
      mindmap: json["mindmap"] ?? "",
      pieChart: json["pie_chart"] ?? "",
      flowchart: json["flowchart"] ?? "",
    );
  }
}

class OpinionCluster {
  final String label;
  final String summary;
  final int mentionCount;

  OpinionCluster({
    required this.label,
    required this.summary,
    required this.mentionCount,
  });

  factory OpinionCluster.fromJson(Map<String, dynamic> json) {
    return OpinionCluster(
      label: json["label"] ?? "",
      summary: json["summary"] ?? "",
      mentionCount: json["mention_count"] ?? 0,
    );
  }
}

class Post {
  final String platform;
  final String? author;
  final String content;
  final String? url;
  final double? sentimentScore;
  final String? sentimentLabel;
  final int? upvotes;
  final int? likes;

  Post({
    required this.platform,
    this.author,
    required this.content,
    this.url,
    this.sentimentScore,
    this.sentimentLabel,
    this.upvotes,
    this.likes,
  });

  factory Post.fromJson(Map<String, dynamic> json) {
    return Post(
      platform: json["platform"],
      author: json["author"],
      content: json["content"],
      url: json["url"],
      sentimentScore: json["sentiment_score"]?.toDouble(),
      sentimentLabel: json["sentiment_label"],
      upvotes: json["upvotes"],
      likes: json["likes"],
    );
  }
}

class Subscription {
  final int id;
  final String keyword;
  final int keywordId;
  final String? platforms;
  final String language;
  final int postLimit;
  final double alertThreshold;
  final int intervalHours;
  final bool isActive;
  final String createdAt;
  final String? lastCheckedAt;
  final String? nextCheckAt;
  final String? userEmail;

  Subscription({
    required this.id,
    required this.keyword,
    required this.keywordId,
    this.platforms,
    required this.language,
    required this.postLimit,
    required this.alertThreshold,
    required this.intervalHours,
    required this.isActive,
    required this.createdAt,
    this.lastCheckedAt,
    this.nextCheckAt,
    this.userEmail,
  });

  factory Subscription.fromJson(Map<String, dynamic> json) {
    return Subscription(
      id: json["id"],
      keyword: json["keyword"],
      keywordId: json["keyword_id"],
      platforms: json["platforms"],
      language: json["language"],
      postLimit: json["post_limit"],
      alertThreshold: json["alert_threshold"]?.toDouble() ?? 30.0,
      intervalHours: json["interval_hours"],
      isActive: json["is_active"],
      createdAt: json["created_at"],
      lastCheckedAt: json["last_checked_at"],
      nextCheckAt: json["next_check_at"],
      userEmail: json["user_email"],
    );
  }
}

class Alert {
  final int id;
  final int subscriptionId;
  final String keyword;
  final double sentimentScore;
  final String? sentimentLabel;
  final int postsCount;
  final int negativePostsCount;
  final String? summary;
  final bool isSent;
  final String createdAt;
  final String? acknowledgedAt;

  Alert({
    required this.id,
    required this.subscriptionId,
    required this.keyword,
    required this.sentimentScore,
    this.sentimentLabel,
    required this.postsCount,
    required this.negativePostsCount,
    this.summary,
    required this.isSent,
    required this.createdAt,
    this.acknowledgedAt,
  });

  factory Alert.fromJson(Map<String, dynamic> json) {
    return Alert(
      id: json["id"],
      subscriptionId: json["subscription_id"],
      keyword: json["keyword"],
      sentimentScore: json["sentiment_score"]?.toDouble() ?? 0.0,
      sentimentLabel: json["sentiment_label"],
      postsCount: json["posts_count"] ?? 0,
      negativePostsCount: json["negative_posts_count"] ?? 0,
      summary: json["summary"],
      isSent: json["is_sent"] ?? false,
      createdAt: json["created_at"],
      acknowledgedAt: json["acknowledged_at"],
    );
  }
}

class ApiService {
  static const String baseUrl = "http://localhost:8000";

  Future<AnalysisResult> analyzeKeyword({
    required String keyword,
    String language = "en",
    List<String>? platforms,
    int limitPerPlatform = 50,
  }) async {
    final response = await http.post(
      Uri.parse("$baseUrl/analyze"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "keyword": keyword,
        "language": language,
        "platforms": platforms,
        "limit_per_platform": limitPerPlatform,
      }),
    );

    if (response.statusCode == 200) {
      return AnalysisResult.fromJson(jsonDecode(response.body));
    } else {
      throw Exception("Failed to analyze keyword: ${response.body}");
    }
  }

  Future<List<Map<String, dynamic>>> getKeywords() async {
    final response = await http.get(Uri.parse("$baseUrl/keywords"));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data["keywords"]);
    } else {
      throw Exception("Failed to fetch keywords");
    }
  }

  // ==================== Subscriptions ====================

  Future<Subscription> createSubscription({
    required String keyword,
    List<String>? platforms,
    String language = "en",
    int postLimit = 50,
    double alertThreshold = 30.0,
    int intervalHours = 6,
    String? userEmail,
  }) async {
    final response = await http.post(
      Uri.parse("$baseUrl/subscriptions"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "keyword": keyword,
        "platforms": platforms,
        "language": language,
        "post_limit": postLimit,
        "alert_threshold": alertThreshold,
        "interval_hours": intervalHours,
        "user_email": userEmail,
      }),
    );

    if (response.statusCode == 200) {
      return Subscription.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error["detail"] ?? "Failed to create subscription");
    }
  }

  Future<List<Subscription>> getSubscriptions() async {
    final response = await http.get(Uri.parse("$baseUrl/subscriptions"));

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => Subscription.fromJson(e)).toList();
    } else {
      throw Exception("Failed to fetch subscriptions");
    }
  }

  Future<Subscription> updateSubscription({
    required int subscriptionId,
    required String keyword,
    List<String>? platforms,
    String language = "en",
    int postLimit = 50,
    double alertThreshold = 30.0,
    int intervalHours = 6,
    String? userEmail,
  }) async {
    final response = await http.put(
      Uri.parse("$baseUrl/subscriptions/$subscriptionId"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "keyword": keyword,
        "platforms": platforms,
        "language": language,
        "post_limit": postLimit,
        "alert_threshold": alertThreshold,
        "interval_hours": intervalHours,
        "user_email": userEmail,
      }),
    );

    if (response.statusCode == 200) {
      return Subscription.fromJson(jsonDecode(response.body));
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error["detail"] ?? "Failed to update subscription");
    }
  }

  Future<void> deleteSubscription(int subscriptionId) async {
    final response = await http.delete(
      Uri.parse("$baseUrl/subscriptions/$subscriptionId"),
    );

    if (response.statusCode != 200) {
      throw Exception("Failed to delete subscription");
    }
  }

  // ==================== Alerts ====================

  Future<List<Alert>> getAlerts({
    int limit = 50,
    bool? acknowledged,
  }) async {
    String queryParams = "limit=$limit";
    if (acknowledged != null) {
      queryParams += "&acknowledged=$acknowledged";
    }

    final response = await http.get(
      Uri.parse("$baseUrl/alerts?$queryParams"),
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => Alert.fromJson(e)).toList();
    } else {
      throw Exception("Failed to fetch alerts");
    }
  }

  Future<void> acknowledgeAlert(int alertId) async {
    final response = await http.patch(
      Uri.parse("$baseUrl/alerts/$alertId/acknowledge"),
    );

    if (response.statusCode != 200) {
      throw Exception("Failed to acknowledge alert");
    }
  }
}
