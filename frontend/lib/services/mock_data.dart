/*
Mock data for UI testing and development.
Use this to test the frontend without connecting to the backend.
*/
import "api_service.dart";

class MockData {
  /// Returns a mock AnalysisResult for testing
  static AnalysisResult getMockAnalysisResult() {
    return AnalysisResult(
      keyword: "iPhone 16 Pro",
      postsCount: 87,
      overallSentiment: 72.5,
      sentimentLabel: "Positive",
      summary: "The iPhone 16 Pro has generated significant discussion across social media platforms. Users are particularly excited about the rumored A18 Pro chip improvements and the potential introduction of a periscope zoom lens. The design changes, including a slightly larger display and new titanium frame options, have been well-received. However, some concerns remain about the potential price increase and whether the improvements justify upgrading from the iPhone 15 Pro. The camera enhancements and battery life improvements are the most frequently mentioned positive points, while the lack of major design evolution is a common criticism. Overall sentiment leans positive, with 65% of posts expressing enthusiasm for the new features.",
      opinionClusters: [
        OpinionCluster(
          label: "Camera & Photography",
          summary: "Users are excited about the improved camera system, especially the rumored 48MP ultra-wide camera and advanced computational photography features. The periscope telephoto lens with 5x-10x optical zoom is a highly anticipated addition.",
          mentionCount: 34,
        ),
        OpinionCluster(
          label: "Performance & Gaming",
          summary: "The A18 Pro chip is generating buzz for promised 20% performance gains and improved ray tracing capabilities. Gamers are particularly interested in the potential for console-quality gaming on mobile.",
          mentionCount: 28,
        ),
        OpinionCluster(
          label: "Price & Value",
          summary: "Discussions about the expected \$1199+ starting price have created mixed reactions. Some feel the premium is justified for the upgrades, while others question if it's worth upgrading from the previous generation.",
          mentionCount: 25,
        ),
      ],
      posts: [
        Post(
          platform: "reddit",
          author: "tech_enthusiast_2024",
          content: "The A18 Pro chip benchmarks are looking insane! If the real-world performance matches these leaks, this could be the biggest generational leap we've seen in years. The ray tracing improvements alone might justify the upgrade for mobile gamers.",
          url: "https://reddit.com/r/iphone/comments/abc123",
          sentimentScore: 85.0,
          sentimentLabel: "Very Positive",
          upvotes: 2453,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "TechReview Daily",
          content: "After testing the camera samples, I'm impressed by the dynamic range and low-light performance. The new 48MP ultra-wide camera finally matches the main sensor quality. Portrait mode photos have noticeably better edge detection too.",
          url: "https://youtube.com/watch?v=xyz789",
          sentimentScore: 78.0,
          sentimentLabel: "Positive",
          upvotes: null,
          likes: 15600,
        ),
        Post(
          platform: "reddit",
          author: "apple_fan_since_07",
          content: "Honestly, \$1199 is getting ridiculous. The titanium frame is nice but is it really worth \$200 more than last year? I wish Apple would focus on battery life instead of premium materials.",
          url: "https://reddit.com/r/iphone/comments/def456",
          sentimentScore: 35.0,
          sentimentLabel: "Mixed",
          upvotes: 892,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "Mobile Insider",
          content: "Battery life tests show about 15% improvement over the 15 Pro. The new power management chip really helps with standby time. Heavy users might finally get through a full day without worrying about charging.",
          url: "https://youtube.com/watch?v=ghi012",
          sentimentScore: 82.0,
          sentimentLabel: "Very Positive",
          upvotes: null,
          likes: 8900,
        ),
        Post(
          platform: "reddit",
          author: "photography_pro",
          content: "The 5x optical zoom is a game changer for mobile photography. Tested some shots today and the detail retention is impressive. However, I do notice some shutter lag in low light conditions that needs to be addressed in software updates.",
          url: "https://reddit.com/r/iphone/comments/jkl345",
          sentimentScore: 68.0,
          sentimentLabel: "Positive",
          upvotes: 567,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "Gadget Gazette",
          content: "iOS 18 exclusive features on the 16 Pro are interesting - the AI-powered photo editing and live voice translation during calls work surprisingly well. These software features really differentiate the Pro models from the standard version.",
          url: "https://youtube.com/watch?v=mno678",
          sentimentScore: 75.0,
          sentimentLabel: "Positive",
          upvotes: null,
          likes: 12300,
        ),
        Post(
          platform: "reddit",
          author: "value_hunter",
          content: "Wait for the spring refresh when they usually drop prices. The initial launch hype always wears off and you can save \$150-200. The phone is good but not \$1200 good IMO.",
          url: "https://reddit.com/r/iphone/comments/pqr901",
          sentimentScore: 45.0,
          sentimentLabel: "Neutral",
          upvotes: 1234,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "Apple Analyst",
          content: "Supply chain reports suggest production constraints on the new titanium frames in grey and blue colors. Silver models might be easier to get at launch. If you want a specific color, pre-order early.",
          url: "https://youtube.com/watch?v=stu234",
          sentimentScore: 55.0,
          sentimentLabel: "Neutral",
          upvotes: null,
          likes: 4500,
        ),
        Post(
          platform: "reddit",
          author: "android_convert",
          content: "Coming from Android, the transition has been smoother than expected. The ecosystem integration is unmatched - Apple Watch, AirPods, and Mac work together seamlessly. But I do miss the customization options.",
          url: "https://reddit.com/r/iphone/comments/vwx567",
          sentimentScore: 70.0,
          sentimentLabel: "Positive",
          upvotes: 721,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "Tech Tips Daily",
          content: "The display brightness now hits 2000 nits outdoors - genuinely usable in direct sunlight. This was my biggest complaint with previous iPhones and they finally fixed it. The ProMotion 120Hz remains smooth as ever.",
          url: "https://youtube.com/watch?v=yza890",
          sentimentScore: 80.0,
          sentimentLabel: "Very Positive",
          upvotes: null,
          likes: 9800,
        ),
      ],
    );
  }

  /// Alternative mock data with negative sentiment
  static AnalysisResult getMockNegativeResult() {
    return AnalysisResult(
      keyword: "Controversial App Update",
      postsCount: 156,
      overallSentiment: 28.5,
      sentimentLabel: "Negative",
      summary: "The latest app update has been met with overwhelmingly negative feedback. Users are frustrated with the complete redesign of the user interface, which has removed many beloved features and made navigation more complicated. Performance issues, including crashes and slow loading times, have been widely reported. The subscription price increase announced alongside this update has further angered the community. Many users are threatening to switch to competitor apps, and some have already started migrating their data. The company's response has been seen as inadequate, with generic apologies failing to address specific concerns.",
      opinionClusters: [
        OpinionCluster(
          label: "UI/UX Problems",
          summary: "Users are struggling with the new interface design. Common complaints include hidden menus, removed features, and confusing navigation patterns. Many long-time users feel alienated by the drastic changes.",
          mentionCount: 67,
        ),
        OpinionCluster(
          label: "Performance Issues",
          summary: "Widespread reports of app crashes, freezing, and significant slowdowns after the update. The app appears to have memory leaks and poor optimization, especially on older devices.",
          mentionCount: 52,
        ),
        OpinionCluster(
          label: "Price & Subscription",
          summary: "The timing of a 30% price increase alongside a problematic update has angered users. Many feel they're paying more for a worse experience, and calls for refunds are growing.",
          mentionCount: 37,
        ),
      ],
      posts: [
        Post(
          platform: "reddit",
          author: "frustrated_user_123",
          content: "This update is absolute garbage. I've been using this app for 3 years and they just destroyed everything that made it good. Can't even find basic settings anymore.",
          url: "https://reddit.com/r/technology/comments/bad123",
          sentimentScore: 15.0,
          sentimentLabel: "Very Negative",
          upvotes: 3421,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "Tech Reviewer",
          content: "In my testing, the app crashes 4-5 times per hour. Memory usage has tripled, and battery drain is unacceptable. Until they fix these critical bugs, I cannot recommend this update.",
          url: "https://youtube.com/watch?v=bad456",
          sentimentScore: 20.0,
          sentimentLabel: "Very Negative",
          upvotes: null,
          likes: 25000,
        ),
        Post(
          platform: "reddit",
          author: "loyal_customer_no_more",
          content: "Increased prices by 30% and gave us a broken app in return. Cancelled my subscription today and switched to [competitor]. The customer service response was basically 'we're looking into it' - totally inadequate.",
          url: "https://reddit.com/r/technology/comments/bad789",
          sentimentScore: 10.0,
          sentimentLabel: "Very Negative",
          upvotes: 2156,
          likes: null,
        ),
      ],
    );
  }

  /// Alternative mock data with neutral sentiment
  static AnalysisResult getMockNeutralResult() {
    return AnalysisResult(
      keyword: "New Programming Language",
      postsCount: 45,
      overallSentiment: 52.0,
      sentimentLabel: "Neutral",
      summary: "Discussions about the new programming language reveal mixed but generally cautious reactions. Developers acknowledge its innovative approach to memory safety and concurrency, which addresses real pain points in existing languages. However, concerns about ecosystem maturity, library support, and learning curve are prevalent. Some see it as a potential competitor to Rust and Go, while others question whether we need another systems programming language. The documentation quality has been praised, but tooling is still in early stages. Enterprise adoption remains uncertain due to the talent pool limitations. Overall, the community is taking a wait-and-see approach, acknowledging promise but wanting to see more real-world usage before committing.",
      opinionClusters: [
        OpinionCluster(
          label: "Technical Features",
          summary: "Developers are discussing the language's unique features, particularly its approach to memory management without garbage collection and its built-in concurrency primitives. Technical opinions are generally positive about the design philosophy.",
          mentionCount: 18,
        ),
        OpinionCluster(
          label: "Ecosystem & Adoption",
          summary: "Concerns dominate about library availability, IDE support, and whether the language will gain enough traction to be viable for production use. Many are hesitant to invest time without clear industry adoption signals.",
          mentionCount: 16,
        ),
        OpinionCluster(
          label: "Learning Curve",
          summary: "Opinions are mixed on whether the language brings enough new concepts to justify the learning investment. Some appreciate the fresh approach, others question if it's sufficiently different from existing options.",
          mentionCount: 11,
        ),
      ],
      posts: [
        Post(
          platform: "reddit",
          author: "systems_dev",
          content: "The type system is actually pretty elegant. Borrow checker without the complexity of Rust's lifetime annotations. But I'll wait until there are more libraries before using it in production.",
          url: "https://reddit.com/r/programming/comments/neu123",
          sentimentScore: 60.0,
          sentimentLabel: "Slightly Positive",
          upvotes: 542,
          likes: null,
        ),
        Post(
          platform: "youtube",
          author: "Code Reviewer",
          content: "Documentation is excellent for a v1.0 language. The examples are clear and the language reference is comprehensive. However, debugging tools are basically non-existent at this point.",
          url: "https://youtube.com/watch?v=neu456",
          sentimentScore: 50.0,
          sentimentLabel: "Neutral",
          upvotes: null,
          likes: 3200,
        ),
        Post(
          platform: "reddit",
          author: "skeptical_dev",
          content: "Do we really need another systems language? Between Rust, Go, C++, and Zig, I'm not seeing what problem this solves that isn't already addressed. Feels like solution in search of a problem.",
          url: "https://reddit.com/r/programming/comments/neu789",
          sentimentScore: 40.0,
          sentimentLabel: "Slightly Negative",
          upvotes: 823,
          likes: null,
        ),
      ],
    );
  }
}
