/*
Web platform Mermaid viewer using iframe.
For Chrome/Desktop browsers.
*/
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

// Unique ID counter for iframes
int _iframeIdCounter = 0;

class MermaidWebViewer extends StatefulWidget {
  final String mermaidCode;
  final String title;
  final double height;

  const MermaidWebViewer({
    super.key,
    required this.mermaidCode,
    required this.title,
    this.height = 400,
  });

  @override
  State<MermaidWebViewer> createState() => _MermaidWebViewerState();
}

class _MermaidWebViewerState extends State<MermaidWebViewer> {
  late html.IFrameElement _iframeElement;
  late String _viewType;
  bool _isLoading = true;
  bool _isRegistered = false;

  @override
  void initState() {
    super.initState();
    _viewType = 'mermaid-iframe-${_iframeIdCounter++}';
    _initializeIframe();
  }

  void _initializeIframe() {
    _iframeElement = html.IFrameElement()
      ..srcdoc = _generateHtml()
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.border = 'none'
      ..onLoad.listen((_) {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      });
  }

  String _generateHtml() {
    // Escape the mermaid code for safe embedding
    final escapedCode = widget.mermaidCode
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;');

    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: white;
            padding: 16px;
            overflow: auto;
        }
        #mermaid-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }
        .error-box {
            color: #c62828;
            background-color: #ffebee;
            border: 1px solid #ef9a9a;
            padding: 16px;
            border-radius: 8px;
            margin: 16px;
            font-size: 14px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div id="loading" class="loading">Rendering diagram...</div>
    <div id="error-container"></div>
    <div id="mermaid-container">
        <pre class="mermaid">
$escapedCode
        </pre>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const loadingEl = document.getElementById('loading');
            const errorContainer = document.getElementById('error-container');
            
            try {
                mermaid.initialize({
                    startOnLoad: false,
                    theme: 'default',
                    securityLevel: 'loose',
                    logLevel: 'error',
                    mindmap: {
                        padding: 16,
                        useMaxWidth: true,
                    },
                    flowchart: {
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'
                    }
                });
                
                mermaid.run().then(function() {
                    loadingEl.style.display = 'none';
                }).catch(function(err) {
                    loadingEl.style.display = 'none';
                    errorContainer.innerHTML = '<div class="error-box"><strong>Render Error:</strong><br>' + err.message + '</div>';
                    console.error('Mermaid render error:', err);
                });
            } catch (e) {
                loadingEl.style.display = 'none';
                errorContainer.innerHTML = '<div class="error-box"><strong>Init Error:</strong><br>' + e.message + '</div>';
                console.error('Mermaid init error:', e);
            }
        });
    </script>
</body>
</html>
''';
  }

  @override
  void didUpdateWidget(MermaidWebViewer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.mermaidCode != widget.mermaidCode) {
      setState(() {
        _isLoading = true;
      });
      _iframeElement.srcdoc = _generateHtml();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    // Register the iframe element on first build
    if (!_isRegistered) {
      _isRegistered = true;
      ui_web.platformViewRegistry.registerViewFactory(
        _viewType,
        (int viewId) => _iframeElement,
      );
    }

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
                Expanded(
                  child: Text(
                    widget.title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 12),
                Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () {
                      setState(() {
                        _isLoading = true;
                      });
                      _iframeElement.srcdoc = _generateHtml();
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

          // Iframe content
          ClipRRect(
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(20),
              bottomRight: Radius.circular(20),
            ),
            child: SizedBox(
              height: widget.height,
              child: Stack(
                children: [
                  HtmlElementView(viewType: _viewType),
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
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _iframeElement.remove();
    super.dispose();
  }
}
