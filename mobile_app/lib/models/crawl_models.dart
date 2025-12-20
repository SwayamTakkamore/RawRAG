/// Request model for crawling a website
class CrawlRequest {
  final String url;

  CrawlRequest({required this.url});

  Map<String, dynamic> toJson() => {'url': url};
}

/// Response model after crawling a website
class CrawlResponse {
  final String sessionId;
  final String status;
  final int pagesIndexed;
  final String? websiteTitle;
  final int? totalLinksFound;
  final String message;

  CrawlResponse({
    required this.sessionId,
    required this.status,
    required this.pagesIndexed,
    this.websiteTitle,
    this.totalLinksFound,
    required this.message,
  });

  factory CrawlResponse.fromJson(Map<String, dynamic> json) {
    return CrawlResponse(
      sessionId: json['session_id'] as String,
      status: json['status'] as String,
      pagesIndexed: json['pages_indexed'] as int,
      websiteTitle: json['website_title'] as String?,
      totalLinksFound: json['total_links_found'] as int?,
      message: json['message'] as String,
    );
  }
}
