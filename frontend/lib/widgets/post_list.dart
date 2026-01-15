/*
Post list widget with modern card design.
Displays source posts with platform branding and sentiment indicators.
*/
import "package:flutter/material.dart";
import "package:url_launcher/url_launcher.dart";
import "../services/api_service.dart";

class PostList extends StatelessWidget {
  final List<Post> posts;

  const PostList({super.key, required this.posts});

  Color _getPlatformColor(String platform) {
    switch (platform) {
      case "reddit":
        return const Color(0xFFFF4500);
      case "youtube":
        return const Color(0xFFFF0000);
      case "twitter":
        return const Color(0xFF1DA1F2);
      default:
        return Colors.grey;
    }
  }

  String _getPlatformName(String platform) {
    switch (platform) {
      case "reddit":
        return "Reddit";
      case "youtube":
        return "YouTube";
      case "twitter":
        return "X/Twitter";
      default:
        return platform;
    }
  }

  IconData _getPlatformIcon(String platform) {
    switch (platform) {
      case "reddit":
        return Icons.forum_outlined;
      case "youtube":
        return Icons.play_circle_filled;
      case "twitter":
        return Icons.alternate_email;
      default:
        return Icons.public;
    }
  }

  Color _getSentimentColor(String? label) {
    switch (label) {
      case "positive":
        return const Color(0xFF4CAF50);
      case "negative":
        return const Color(0xFFF44336);
      default:
        return const Color(0xFFFF9800);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: posts.map((post) {
        final platformColor = _getPlatformColor(post.platform);
        final sentimentColor = _getSentimentColor(post.sentimentLabel);

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
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
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: post.url != null
                  ? () async {
                      final uri = Uri.parse(post.url!);
                      if (await canLaunchUrl(uri)) {
                        await launchUrl(uri, mode: LaunchMode.externalApplication);
                      }
                    }
                  : null,
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header row
                    Row(
                      children: [
                        // Platform icon
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: platformColor.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            _getPlatformIcon(post.platform),
                            color: platformColor,
                            size: 18,
                          ),
                        ),
                        const SizedBox(width: 10),
                        // Platform name
                        Text(
                          _getPlatformName(post.platform),
                          style: TextStyle(
                            color: platformColor,
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const Spacer(),
                        // Sentiment badge
                        if (post.sentimentLabel != null)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: sentimentColor.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              post.sentimentLabel!.toUpperCase(),
                              style: TextStyle(
                                color: sentimentColor,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                letterSpacing: 0.8,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    // Content
                    Text(
                      post.content,
                      maxLines: 4,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 14,
                        height: 1.6,
                        color: Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 12),
                    // Footer row
                    Row(
                      children: [
                        // Author
                        if (post.author != null) ...[
                          Icon(Icons.person_outline, size: 14, color: Colors.grey[500]),
                          const SizedBox(width: 4),
                          Text(
                            post.author!,
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(width: 12),
                        ],
                        // Upvotes
                        if (post.upvotes != null && post.upvotes! > 0) ...[
                          Icon(Icons.arrow_upward, size: 14, color: Colors.grey[500]),
                          const SizedBox(width: 4),
                          Text(
                            _formatNumber(post.upvotes!),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(width: 12),
                        ],
                        // Likes
                        if (post.likes != null && post.likes! > 0) ...[
                          Icon(Icons.favorite_border, size: 14, color: Colors.grey[500]),
                          const SizedBox(width: 4),
                          Text(
                            _formatNumber(post.likes!),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(width: 12),
                        ],
                        const Spacer(),
                        // Link indicator
                        if (post.url != null)
                          Icon(
                            Icons.open_in_new,
                            size: 16,
                            color: Colors.grey[400],
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  String _formatNumber(int num) {
    if (num >= 1000000) {
      return "${(num / 1000000).toStringAsFixed(1)}M";
    } else if (num >= 1000) {
      return "${(num / 1000).toStringAsFixed(1)}K";
    }
    return num.toString();
  }
}
