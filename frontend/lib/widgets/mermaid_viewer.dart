/*
Widget for rendering Mermaid diagrams using WebView.
Displays mind maps, flow charts, and pie charts.
*/
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:webview_flutter/webview_flutter.dart';

class MermaidViewer extends StatefulWidget {
  final String mermaidCode;
  final String title;
  final double height;

  const MermaidViewer({
    super.key,
    required this.mermaidCode,
    required this.title,
    this.height = 400,
  });

  @override
  State<MermaidViewer> createState() => _MermaidViewerState();
}

class _MermaidViewerState extends State<MermaidViewer> {
  late final WebViewController _controller;
  bool _isLoading = true;
  String? _errorMessage;
  String _debugInfo = "";

  @override
  void initState() {
    super.initState();
    _initWebView();
  }

  void _initWebView() async {
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0x00000000))
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (String url) {
            if (kDebugMode) {
              setState(() {
                _debugInfo = "Page loading: $url";
              });
            }
          },
          onPageFinished: (String url) {
            if (kDebugMode) {
              setState(() {
                _debugInfo = "Page loaded: $url";
                _isLoading = false;
              });
            } else {
              setState(() {
                _isLoading = false;
              });
            }
          },
          onWebResourceError: (WebResourceError error) {
            if (kDebugMode) {
              setState(() {
                _errorMessage = "Error: ${error.description} (code: ${error.errorCode})";
                _debugInfo = "Resource failed: ${error.errorCode}";
                _isLoading = false;
              });
            } else {
              setState(() {
                _errorMessage = error.description;
                _isLoading = false;
              });
            }
          },
          onNavigationRequest: (NavigationRequest request) {
            if (kDebugMode) {
              print("Navigation request: ${request.url}");
            }
            return NavigationDecision.navigate;
          },
        ),
      )
      ..loadHtmlString(_generateHtml());
  }

  String _generateHtml() {
    // Escape the mermaid code properly
    final escapedCode = widget.mermaidCode
        .replaceAll('\n', '\\n')
        .replaceAll("'", "\\'")
        .replaceAll('"', '\\"');

    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
    <style>
        body {
            margin: 0;
            padding: 16px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #ffffff;
            overflow: auto;
        }
        .mermaid {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 300px;
        }
        .error {
            color: #721c24;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 16px;
            border-radius: 4px;
            margin: 16px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div id="loading" class="loading">Loading diagram...</div>
    <div id="error" class="error" style="display: none;"></div>
    <pre class="mermaid">
${widget.mermaidCode}
    </pre>

    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js"></script>
    <script>
        window.addEventListener('load', function() {
            console.log('Page loaded, initializing Mermaid...');

            mermaid.initialize({
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                logLevel: 'debug',
                mindmap: {
                    padding: 10,
                    useMaxWidth: true,
                },
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }
            });

            // Hide loading, show diagram
            setTimeout(function() {
                document.getElementById('loading').style.display = 'none';
            }, 1000);

            console.log('Mermaid initialized');
        });

        // Error handling
        window.addEventListener('error', function(e) {
            console.error('JavaScript error:', e);
            var errorDiv = document.getElementById('error');
            errorDiv.textContent = 'Error: ' + e.message;
            errorDiv.style.display = 'block';
            document.getElementById('loading').style.display = 'none';
        });
    </script>
</body>
</html>
''';
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: colorScheme.primary,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
              ),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.account_tree,
                  color: Colors.white,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Text(
                  widget.title,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const Spacer(),
                // Refresh button
                Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () {
                      setState(() {
                        _isLoading = true;
                        _errorMessage = null;
                      });
                      _controller.reload();
                    },
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.refresh,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // WebView content
          ClipRRect(
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(20),
              bottomRight: Radius.circular(20),
            ),
            child: SizedBox(
              height: widget.height,
              child: Stack(
                children: [
                  WebViewWidget(controller: _controller),
                  if (_isLoading)
                    Container(
                      color: Colors.white.withOpacity(0.9),
                      child: const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            CircularProgressIndicator(),
                            SizedBox(height: 16),
                            Text(
                              "Loading diagram...",
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  if (_errorMessage != null)
                    Container(
                      color: Colors.white,
                      child: Center(
                        child: SingleChildScrollView(
                          padding: const EdgeInsets.all(32),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.error_outline,
                                size: 48,
                                color: Colors.red[300],
                              ),
                              const SizedBox(height: 16),
                              Text(
                                _errorMessage!,
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[700],
                                ),
                              ),
                              if (_debugInfo.isNotEmpty) ...[
                                const SizedBox(height: 8),
                                Text(
                                  "Debug: $_debugInfo",
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[500],
                                    fontStyle: FontStyle.italic,
                                  ),
                                ),
                              ],
                              const SizedBox(height: 16),
                              ElevatedButton.icon(
                                onPressed: () {
                                  setState(() {
                                    _errorMessage = null;
                                    _isLoading = true;
                                    _debugInfo = "";
                                  });
                                  _controller.reload();
                                },
                                icon: const Icon(Icons.refresh),
                                label: const Text("Retry"),
                              ),
                              const SizedBox(height: 16),
                              // Show mermaid code for debugging
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.grey[100],
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: Colors.grey[300]!),
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      "Mermaid Code (debug):",
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.grey[700],
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      widget.mermaidCode,
                                      style: TextStyle(
                                        fontSize: 10,
                                        fontFamily: 'monospace',
                                        color: Colors.grey[800],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
