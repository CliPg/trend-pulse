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

  AnalysisResult({
    required this.keyword,
    required this.postsCount,
    required this.overallSentiment,
    required this.sentimentLabel,
    required this.summary,
    required this.opinionClusters,
    required this.posts,
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
}
