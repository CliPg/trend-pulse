/*
Beautiful Mind Map viewer using ECharts.
For Chrome/Desktop browsers.
*/
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;
import 'package:flutter/material.dart';

// Unique ID counter for iframes
int _echartsIdCounter = 0;

class MindMapViewer extends StatefulWidget {
  final String treeData; // JSON string of tree data
  final String title;
  final double height;

  const MindMapViewer({
    super.key,
    required this.treeData,
    required this.title,
    this.height = 500,
  });

  @override
  State<MindMapViewer> createState() => _MindMapViewerState();
}

class _MindMapViewerState extends State<MindMapViewer> {
  late html.IFrameElement _iframeElement;
  late String _viewType;
  bool _isLoading = true;
  bool _isRegistered = false;

  @override
  void initState() {
    super.initState();
    _viewType = 'echarts-mindmap-${_echartsIdCounter++}';
    _initializeIframe();
  }

  void _initializeIframe() {
    _iframeElement = html.IFrameElement()
      ..srcdoc = _generateHtml()
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.border = 'none'
      ..style.pointerEvents = 'none'
      ..onLoad.listen((_) {
        if (mounted) {
          setState(() {
            _isLoading = false;
          });
        }
      });
  }

  String _generateHtml() {
    // The treeData is already a JSON string from backend
    final treeDataJson = widget.treeData;

    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mind Map</title>
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
            background: linear-gradient(135deg, #fafbfc 0%, #f0f4f8 100%);
        }
        #chart {
            width: 100%;
            height: 100%;
        }
        .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #64748b;
            font-size: 15px;
        }
        .error-box {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #dc2626;
            background: #fef2f2;
            border: 1px solid #fecaca;
            padding: 20px 30px;
            border-radius: 12px;
            font-size: 14px;
            text-align: center;
            max-width: 80%;
        }
    </style>
</head>
<body>
    <div id="loading" class="loading">
        <div style="margin-bottom: 12px;">
            <svg width="40" height="40" viewBox="0 0 40 40">
                <circle cx="20" cy="20" r="16" fill="none" stroke="#e2e8f0" stroke-width="4"/>
                <circle cx="20" cy="20" r="16" fill="none" stroke="#6366f1" stroke-width="4" 
                    stroke-dasharray="75 25" stroke-linecap="round">
                    <animateTransform attributeName="transform" type="rotate" 
                        from="0 20 20" to="360 20 20" dur="1s" repeatCount="indefinite"/>
                </circle>
            </svg>
        </div>
        Generating mind map...
    </div>
    <div id="chart"></div>
    <div id="error-container"></div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const loadingEl = document.getElementById('loading');
            const errorContainer = document.getElementById('error-container');
            const chartEl = document.getElementById('chart');
            
            try {
                const treeData = $treeDataJson;
                
                const chart = echarts.init(chartEl);
                
                const option = {
                    backgroundColor: 'transparent',
                    tooltip: {
                        trigger: 'item',
                        backgroundColor: 'rgba(255, 255, 255, 0.98)',
                        borderColor: '#e2e8f0',
                        borderWidth: 1,
                        borderRadius: 12,
                        padding: [12, 16],
                        textStyle: {
                            color: '#334155',
                            fontSize: 13
                        },
                        formatter: function(params) {
                            return '<strong>' + params.name + '</strong>';
                        }
                    },
                    series: [{
                        type: 'tree',
                        data: [treeData],
                        layout: 'orthogonal',
                        orient: 'LR',
                        symbol: 'circle',
                        symbolSize: 12,
                        initialTreeDepth: 3,
                        animationDuration: 800,
                        animationEasing: 'cubicOut',
                        roam: false,
                        top: '5%',
                        bottom: '5%',
                        left: '12%',
                        right: '25%',
                        label: {
                            show: true,
                            position: 'right',
                            verticalAlign: 'middle',
                            distance: 10,
                            fontSize: 13,
                            fontWeight: 500,
                            color: '#334155',
                            formatter: function(params) {
                                const name = params.name || '';
                                if (name.length > 30) {
                                    return name.substring(0, 27) + '...';
                                }
                                return name;
                            }
                        },
                        leaves: {
                            label: {
                                position: 'right',
                                verticalAlign: 'middle',
                                fontSize: 12,
                                fontWeight: 400,
                                color: '#64748b'
                            }
                        },
                        expandAndCollapse: false,
                        itemStyle: {
                            color: '#6366f1',
                            borderColor: '#4f46e5',
                            borderWidth: 2,
                            shadowColor: 'rgba(99, 102, 241, 0.25)',
                            shadowBlur: 8
                        },
                        lineStyle: {
                            color: '#c7d2fe',
                            width: 2,
                            curveness: 0.5
                        },
                        emphasis: {
                            focus: 'descendant',
                            itemStyle: {
                                color: '#4f46e5',
                                borderColor: '#3730a3',
                                shadowBlur: 15,
                                shadowColor: 'rgba(99, 102, 241, 0.4)'
                            },
                            lineStyle: {
                                width: 3,
                                color: '#6366f1'
                            },
                            label: {
                                fontSize: 14,
                                fontWeight: 600
                            }
                        }
                    }]
                };
                
                chart.setOption(option);
                loadingEl.style.display = 'none';
                
                // Handle resize
                window.addEventListener('resize', function() {
                    chart.resize();
                });
                
            } catch (e) {
                loadingEl.style.display = 'none';
                errorContainer.innerHTML = '<div class="error-box"><strong>⚠️ Error</strong><br><br>' + e.message + '</div>';
                console.error('ECharts error:', e);
            }
        });
    </script>
</body>
</html>
''';
  }

  @override
  void didUpdateWidget(MindMapViewer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.treeData != widget.treeData) {
      setState(() {
        _isLoading = true;
      });
      _iframeElement.srcdoc = _generateHtml();
    }
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

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
            color: const Color(0xFF6366f1).withOpacity(0.1),
            blurRadius: 30,
            offset: const Offset(0, 10),
          ),
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with gradient
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF6366f1), Color(0xFF8b5cf6)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.only(
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
                    Icons.hub_rounded,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.title,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                          letterSpacing: -0.5,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Opinion Clusters Mind Map',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white.withOpacity(0.85),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                _buildActionButton(
                  icon: Icons.refresh_rounded,
                  onTap: () {
                    setState(() {
                      _isLoading = true;
                    });
                    _iframeElement.srcdoc = _generateHtml();
                  },
                ),
              ],
            ),
          ),

          // Chart content
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
                        color: Colors.white.withOpacity(0.98),
                      ),
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 48,
                              height: 48,
                              child: CircularProgressIndicator(
                                strokeWidth: 3,
                                valueColor: const AlwaysStoppedAnimation<Color>(
                                  Color(0xFF6366f1),
                                ),
                              ),
                            ),
                            const SizedBox(height: 20),
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

  Widget _buildActionButton({
    required IconData icon,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.15),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: Colors.white.withOpacity(0.25),
              width: 1,
            ),
          ),
          child: Icon(
            icon,
            color: Colors.white,
            size: 20,
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _iframeElement.remove();
    super.dispose();
  }
}
