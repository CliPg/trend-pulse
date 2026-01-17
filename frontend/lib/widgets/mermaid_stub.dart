/*
Stub implementation for non-web platforms.
This file is used when dart:html is not available.
*/
import 'package:flutter/material.dart';

class MermaidWebViewer extends StatelessWidget {
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
  Widget build(BuildContext context) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(20),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.warning, size: 48, color: Colors.orange[700]),
            const SizedBox(height: 16),
            Text(
              'Web-only feature',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Mermaid diagrams are only available on web browsers',
              style: TextStyle(fontSize: 14, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
