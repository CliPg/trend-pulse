/*
Post list widget with platform grouping and modern card design.
Displays source posts grouped by platform with collapsible sections.
*/
import "package:flutter/material.dart";
import "package:url_launcher/url_launcher.dart";
import "../services/api_service.dart";

class PostList extends StatefulWidget {
  final List<Post> posts;

  const PostList({super.key, required this.posts});

  @override
  State<PostList> createState() => _PostListState();
}

class _PostListState extends State<PostList> {
  // Track expanded state for each platform
  final Map<String, bool> _expandedPlatforms = {};

  @override
  void initState() {
    super.initState();
    // Default all platforms to expanded
    for (var post in widget.posts) {
      _expandedPlatforms.putIfAbsent(post.platform, () => true);
    }
  }

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

  Map<String, List<Post>> _groupPostsByPlatform() {
    final grouped = <String, List<Post>>{};
    for (var post in widget.posts) {
      grouped.putIfAbsent(post.platform, () => []).add(post);
    }
    return grouped;
  }

  @override
  Widget build(BuildContext context) {
    final groupedPosts = _groupPostsByPlatform();

    return Column(
      children: groupedPosts.entries.map((entry) {
        final platform = entry.key;
        final posts = entry.value;
        final platformColor = _getPlatformColor(platform);
        final isExpanded = _expandedPlatforms[platform] ?? true;

        return Container(
          margin: const EdgeInsets.only(bottom: 20),
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
              // Platform header
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () {
                    setState(() {
                      _expandedPlatforms[platform] = !isExpanded;
                    });
                  },
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          platformColor.withOpacity(0.08),
                          platformColor.withOpacity(0.03),
                        ],
                      ),
                      borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                    ),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: platformColor.withOpacity(0.15),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Icon(
                            _getPlatformIcon(platform),
                            color: platformColor,
                            size: 24,
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _getPlatformName(platform),
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: platformColor,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                "${posts.length} ${posts.length == 1 ? 'post' : 'posts'}",
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          isExpanded ? Icons.expand_less : Icons.expand_more,
                          color: platformColor,
                          size: 28,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
              // Posts list
              if (isExpanded)
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: posts.asMap().entries.map((entry) {
                      final index = entry.key;
                      final post = entry.value;
                      final isLast = index == posts.length - 1;

                      return _buildPostCard(post, platformColor, isLast);
                    }).toList(),
                  ),
                ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildPostCard(Post post, Color platformColor, bool isLast) {
    final sentimentColor = _getSentimentColor(post.sentimentLabel);

    return Container(
      margin: EdgeInsets.only(bottom: isLast ? 0 : 12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.grey[200]!,
          width: 1,
        ),
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
                    ],
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
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
