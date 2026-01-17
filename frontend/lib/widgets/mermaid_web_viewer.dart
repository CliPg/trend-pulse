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
      ..style.pointerEvents = 'none'  // Disable pointer events to allow parent scrolling
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
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }
        #mermaid-container {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
        }
        .mermaid {
            font-size: 16px !important;
        }
        .mermaid svg {
            max-width: 100%;
            height: auto;
        }
        /* Mindmap specific styles */
        .mermaid .mindmap-node rect {
            rx: 12px;
            ry: 12px;
        }
        .mermaid .mindmap-node text {
            font-size: 14px !important;
            font-weight: 500;
        }
        .error-box {
            color: #c62828;
            background-color: #ffebee;
            border: 1px solid #ef9a9a;
            padding: 20px;
            border-radius: 12px;
            margin: 20px;
            font-size: 14px;
            max-width: 400px;
            text-align: center;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #64748b;
            font-size: 16px;
        }
        .loading::after {
            content: '';
            animation: dots 1.5s infinite;
        }
        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
    </style>
</head>
<body>
    <div id="loading" class="loading">Rendering diagram</div>
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
                    theme: 'base',
                    securityLevel: 'loose',
                    logLevel: 'error',
                    themeVariables: {
                        primaryColor: '#6366f1',
                        primaryTextColor: '#ffffff',
                        primaryBorderColor: '#4f46e5',
                        lineColor: '#94a3b8',
                        secondaryColor: '#f1f5f9',
                        tertiaryColor: '#e0e7ff',
                        fontFamily: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
                        fontSize: '16px'
                    },
                    mindmap: {
                        padding: 20,
                        useMaxWidth: false,
                    },
                    flowchart: {
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis'
                    }
                });
                
                mermaid.run().then(function() {
                    loadingEl.style.display = 'none';
                    // Scale the SVG to fit better
                    const svg = document.querySelector('.mermaid svg');
                    if (svg) {
                        svg.style.maxHeight = '100%';
                        svg.style.width = 'auto';
                    }
                }).catch(function(err) {
                    loadingEl.style.display = 'none';
                    errorContainer.innerHTML = '<div class="error-box"><strong>⚠️ Render Error</strong><br><br>' + err.message + '</div>';
                    console.error('Mermaid render error:', err);
                });
            } catch (e) {
                loadingEl.style.display = 'none';
                errorContainer.innerHTML = '<div class="error-box"><strong>⚠️ Init Error</strong><br><br>' + e.message + '</div>';
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
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: colorScheme.primary.withOpacity(0.08),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with gradient
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 18),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  colorScheme.primary,
                  colorScheme.primary.withOpacity(0.85),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(24),
                topRight: Radius.circular(24),
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.hub,
                    color: Colors.white,
                    size: 22,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.title,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                          letterSpacing: -0.3,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Opinion Clusters Visualization',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.white.withOpacity(0.8),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
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
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.white.withOpacity(0.2),
                          width: 1,
                        ),
                      ),
                      child: const Icon(
                        Icons.refresh_rounded,
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
              bottomLeft: Radius.circular(24),
              bottomRight: Radius.circular(24),
            ),
            child: SizedBox(
              height: widget.height,
              child: Stack(
                children: [
                  HtmlElementView(viewType: _viewType),
                  if (_isLoading)
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.95),
                        borderRadius: const BorderRadius.only(
                          bottomLeft: Radius.circular(24),
                          bottomRight: Radius.circular(24),
                        ),
                      ),
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 40,
                              height: 40,
                              child: CircularProgressIndicator(
                                strokeWidth: 3,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  colorScheme.primary,
                                ),
                              ),
                            ),
                            const SizedBox(height: 16),
                            Text(
                              "Generating mind map...",
                              style: TextStyle(
                                fontSize: 15,
                                color: Colors.grey[600],
                                fontWeight: FontWeight.w500,
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
