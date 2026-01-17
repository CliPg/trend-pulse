/*
Beautiful Mind Map viewer using ECharts.
For Chrome/Desktop browsers.
*/
import 'dart:html' as html;
import 'dart:ui_web' as ui_web;
import 'package:flutter/gestures.dart';
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
  html.EventListener? _messageListener;

  @override
  void initState() {
    super.initState();
    _viewType = 'echarts-mindmap-${_echartsIdCounter++}';
    _initializeIframe();
    _setupMessageListener();
  }

  void _setupMessageListener() {
    _messageListener = (html.Event event) {
      if (event is html.MessageEvent) {
        final data = event.data;
        if (data is Map && data['type'] == 'wheel') {
          // Forward scroll to parent document
          final deltaY = (data['deltaY'] as num?)?.toDouble() ?? 0;
          html.window.scrollBy(0, deltaY.toInt());
        }
      }
    };
    html.window.addEventListener('message', _messageListener!);
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
            position: relative;
        }
        #chart {
            width: 100%;
            height: 100%;
            cursor: grab;
        }
        #chart:active {
            cursor: grabbing;
        }
        .drag-hint {
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: rgba(99, 102, 241, 0.9);
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 11px;
            color: white;
            display: flex;
            align-items: center;
            gap: 5px;
            pointer-events: none;
            opacity: 0.85;
        }
        .zoom-controls {
            position: absolute;
            top: 12px;
            right: 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            z-index: 1000;
        }
        .zoom-btn {
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 18px;
            font-weight: 600;
            color: #6366f1;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        .zoom-btn:hover {
            background: white;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .zoom-btn:active {
            transform: scale(0.95);
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
    <div class="zoom-controls">
        <button class="zoom-btn" id="zoomIn" title="放大">+</button>
        <button class="zoom-btn" id="zoomOut" title="缩小">−</button>
        <button class="zoom-btn" id="zoomReset" title="重置">⟲</button>
    </div>
    <div class="drag-hint">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M12 12h0"/>
        </svg>
        Drag · Scroll
    </div>

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
                        borderRadius: 10,
                        padding: [10, 14],
                        textStyle: {
                            color: '#334155',
                            fontSize: 12
                        },
                        formatter: function(params) {
                            return '<div style="max-width:280px;word-wrap:break-word;"><strong>' + params.name + '</strong></div>';
                        }
                    },
                    series: [{
                        type: 'tree',
                        data: [treeData],
                        layout: 'orthogonal',
                        orient: 'LR',
                        symbol: 'circle',
                        symbolSize: 10,
                        initialTreeDepth: 3,
                        animationDuration: 600,
                        animationEasing: 'cubicOut',
                        roam: true,
                        zoom: 1.0,
                        top: '5%',
                        bottom: '5%',
                        left: '8%',
                        right: '15%',
                        nodeGap: 18,
                        layerPadding: 80,
                        label: {
                            show: true,
                            position: 'right',
                            verticalAlign: 'middle',
                            distance: 8,
                            fontSize: 12,
                            fontWeight: 500,
                            color: '#334155',
                            formatter: function(params) {
                                return params.name || '';
                            }
                        },
                        leaves: {
                            label: {
                                position: 'right',
                                verticalAlign: 'middle',
                                fontSize: 11,
                                fontWeight: 400,
                                color: '#64748b'
                            }
                        },
                        expandAndCollapse: false,
                        itemStyle: {
                            color: '#6366f1',
                            borderColor: '#4f46e5',
                            borderWidth: 2,
                            shadowColor: 'rgba(99, 102, 241, 0.2)',
                            shadowBlur: 6
                        },
                        lineStyle: {
                            color: '#c7d2fe',
                            width: 1.5,
                            curveness: 0.3
                        },
                        emphasis: {
                            focus: 'descendant',
                            itemStyle: {
                                color: '#4f46e5',
                                borderColor: '#3730a3',
                                shadowBlur: 10,
                                shadowColor: 'rgba(99, 102, 241, 0.35)'
                            },
                            lineStyle: {
                                width: 2,
                                color: '#818cf8'
                            },
                            label: {
                                fontSize: 13,
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

                // Zoom controls
                const zoomInBtn = document.getElementById('zoomIn');
                const zoomOutBtn = document.getElementById('zoomOut');
                const zoomResetBtn = document.getElementById('zoomReset');

                zoomInBtn.addEventListener('click', function() {
                    const currentOption = chart.getOption();
                    const currentZoom = currentOption.series[0].zoom || 1.0;
                    chart.setOption({
                        series: [{
                            zoom: Math.min(currentZoom + 0.2, 3.0)
                        }]
                    });
                });

                zoomOutBtn.addEventListener('click', function() {
                    const currentOption = chart.getOption();
                    const currentZoom = currentOption.series[0].zoom || 1.0;
                    chart.setOption({
                        series: [{
                            zoom: Math.max(currentZoom - 0.2, 0.3)
                        }]
                    });
                });

                zoomResetBtn.addEventListener('click', function() {
                    chart.setOption({
                        series: [{
                            zoom: 1.0
                        }]
                    });
                });

                // Forward wheel events to parent for page scrolling
                chartEl.addEventListener('wheel', function(e) {
                    window.parent.postMessage({
                        type: 'wheel',
                        deltaY: e.deltaY,
                        deltaX: e.deltaX
                    }, '*');
                }, { passive: true });
                
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
                  icon: Icons.open_in_full_rounded,
                  tooltip: '全屏查看',
                  onTap: () => _showFullScreenDialog(context),
                ),
                const SizedBox(width: 8),
                _buildActionButton(
                  icon: Icons.refresh_rounded,
                  tooltip: '刷新',
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

          // Chart content with interaction hint - 使用透明覆盖层拦截滚动
          ClipRRect(
            borderRadius: const BorderRadius.only(
              bottomLeft: Radius.circular(24),
              bottomRight: Radius.circular(24),
            ),
            child: _ScrollBlocker(
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
  
  void _showFullScreenDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(16),
        child: Container(
          width: MediaQuery.of(context).size.width * 0.95,
          height: MediaQuery.of(context).size.height * 0.9,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
          ),
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
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
                    const Icon(Icons.hub_rounded, color: Colors.white, size: 24),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        '${widget.title} - Mind Map',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    IconButton(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.close_rounded, color: Colors.white),
                    ),
                  ],
                ),
              ),
              // Full screen chart
              Expanded(
                child: ClipRRect(
                  borderRadius: const BorderRadius.only(
                    bottomLeft: Radius.circular(24),
                    bottomRight: Radius.circular(24),
                  ),
                  child: _FullScreenMindMap(treeData: widget.treeData),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String tooltip,
    required VoidCallback onTap,
  }) {
    return Tooltip(
      message: tooltip,
      child: Material(
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
      ),
    );
  }

  @override
  void dispose() {
    if (_messageListener != null) {
      html.window.removeEventListener('message', _messageListener!);
    }
    _iframeElement.remove();
    super.dispose();
  }
}

// Full screen mind map widget for dialog
class _FullScreenMindMap extends StatefulWidget {
  final String treeData;
  
  const _FullScreenMindMap({required this.treeData});
  
  @override
  State<_FullScreenMindMap> createState() => _FullScreenMindMapState();
}

class _FullScreenMindMapState extends State<_FullScreenMindMap> {
  late html.IFrameElement _iframeElement;
  late String _viewType;
  bool _isRegistered = false;
  
  @override
  void initState() {
    super.initState();
    _viewType = 'echarts-fullscreen-${_echartsIdCounter++}';
    _initializeIframe();
  }
  
  void _initializeIframe() {
    _iframeElement = html.IFrameElement()
      ..srcdoc = _generateHtml()
      ..style.width = '100%'
      ..style.height = '100%'
      ..style.border = 'none';
  }
  
  String _generateHtml() {
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { width: 100%; height: 100%; overflow: hidden; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #fafbfc 0%, #f0f4f8 100%);
        }
        #chart { width: 100%; height: 100%; cursor: grab; }
        #chart:active { cursor: grabbing; }
        .zoom-controls {
            position: absolute;
            top: 12px;
            right: 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            z-index: 1000;
        }
        .zoom-btn {
            width: 36px;
            height: 36px;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 20px;
            font-weight: 600;
            color: #6366f1;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }
        .zoom-btn:hover {
            background: white;
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .zoom-btn:active {
            transform: scale(0.95);
        }
        .hint {
            position: absolute;
            bottom: 16px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(99, 102, 241, 0.9);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            color: white;
        }
    </style>
</head>
<body>
    <div id="chart"></div>
    <div class="zoom-controls">
        <button class="zoom-btn" id="zoomIn" title="放大">+</button>
        <button class="zoom-btn" id="zoomOut" title="缩小">−</button>
        <button class="zoom-btn" id="zoomReset" title="重置">⟲</button>
    </div>
    <div class="hint">Drag · Scroll · Pinch</div>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script>
        const treeData = ${widget.treeData};
        const chart = echarts.init(document.getElementById('chart'));
        chart.setOption({
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(255,255,255,0.98)',
                borderColor: '#e2e8f0',
                borderRadius: 10,
                padding: [10, 14],
                textStyle: { color: '#334155', fontSize: 13 },
                formatter: p => '<div style="max-width:350px;word-wrap:break-word;"><strong>' + p.name + '</strong></div>'
            },
            series: [{
                type: 'tree',
                data: [treeData],
                layout: 'orthogonal',
                orient: 'LR',
                symbol: 'circle',
                symbolSize: 12,
                initialTreeDepth: 4,
                roam: true,
                zoom: 1.0,
                top: '5%',
                bottom: '5%',
                left: '8%',
                right: '15%',
                nodeGap: 20,
                layerPadding: 100,
                label: {
                    show: true,
                    position: 'right',
                    distance: 10,
                    fontSize: 13,
                    fontWeight: 500,
                    color: '#334155'
                },
                leaves: {
                    label: { fontSize: 12, color: '#64748b' }
                },
                itemStyle: {
                    color: '#6366f1',
                    borderColor: '#4f46e5',
                    borderWidth: 2
                },
                lineStyle: {
                    color: '#c7d2fe',
                    width: 1.5,
                    curveness: 0.3
                },
                emphasis: {
                    focus: 'descendant',
                    itemStyle: { color: '#4f46e5' },
                    label: { fontSize: 14, fontWeight: 600 }
                }
            }]
        });

        // Zoom controls
        const zoomInBtn = document.getElementById('zoomIn');
        const zoomOutBtn = document.getElementById('zoomOut');
        const zoomResetBtn = document.getElementById('zoomReset');

        zoomInBtn.addEventListener('click', function() {
            const currentOption = chart.getOption();
            const currentZoom = currentOption.series[0].zoom || 1.0;
            chart.setOption({
                series: [{
                    zoom: Math.min(currentZoom + 0.2, 3.0)
                }]
            });
        });

        zoomOutBtn.addEventListener('click', function() {
            const currentOption = chart.getOption();
            const currentZoom = currentOption.series[0].zoom || 1.0;
            chart.setOption({
                series: [{
                    zoom: Math.max(currentZoom - 0.2, 0.3)
                }]
            });
        });

        zoomResetBtn.addEventListener('click', function() {
            chart.setOption({
                series: [{
                    zoom: 1.0
                }]
            });
        });

        window.addEventListener('resize', () => chart.resize());
    </script>
</body>
</html>
''';
  }
  
  @override
  Widget build(BuildContext context) {
    if (!_isRegistered) {
      _isRegistered = true;
      ui_web.platformViewRegistry.registerViewFactory(
        _viewType,
        (int viewId) => _iframeElement,
      );
    }
    return HtmlElementView(viewType: _viewType);
  }
  
  @override
  void dispose() {
    _iframeElement.remove();
    super.dispose();
  }
}

/// 简单包装器，不阻止页面滚动
class _ScrollBlocker extends StatelessWidget {
  final Widget child;
  final double height;

  const _ScrollBlocker({required this.child, required this.height});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      child: child,
    );
  }
}