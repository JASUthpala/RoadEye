import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

void main() {
  runApp(const SmartHelmetApp());
}

class SmartHelmetApp extends StatelessWidget {
  const SmartHelmetApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Smart Helmet',
      theme: ThemeData.dark(),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String connectionText = 'Helmet Not Connected';
  double speed = 0.0;

  @override
  void initState() {
    super.initState();
    // Fake speed update every second
    Future.delayed(const Duration(seconds: 1), updateSpeed);
  }

  void updateSpeed() {
    setState(() {
      speed += 5; // increase by 5 km/h
      if (speed > 100) speed = 0; // reset after 100
    });
    Future.delayed(const Duration(seconds: 1), updateSpeed);
  }

  void scanForHelmet() async {
    setState(() {
      connectionText = 'Scanning...';
    });

    // Start scanning (static method)
    FlutterBluePlus.startScan(timeout: const Duration(seconds: 4));

    // Listen to scan results (static getter)
    FlutterBluePlus.scanResults.listen((results) {
      for (ScanResult r in results) {
        print('${r.device.name} found! rssi: ${r.rssi}');
        // Replace 'ESP32Helmet' with your device name
        if (r.device.name == 'ESP32Helmet') {
          setState(() {
            connectionText = 'Helmet Found: ${r.device.name}';
          });
          FlutterBluePlus.stopScan();
          break;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Helmet Dashboard'),
        centerTitle: true,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.security, size: 80),
            const SizedBox(height: 20),
            Text(connectionText, style: const TextStyle(fontSize: 20)),
            const SizedBox(height: 20),
            Text(
              'Speed: ${speed.toStringAsFixed(1)} km/h',
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 30),
            ElevatedButton(
              onPressed: scanForHelmet,
              child: const Text('Connect Helmet'),
            ),
          ],
        ),
      ),
    );
  }
}
