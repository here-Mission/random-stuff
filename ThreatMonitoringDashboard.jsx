// ThreatMonitoringDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

const ThreatMonitoringDashboard = () => {
  const [sandboxStatus, setSandboxStatus] = useState({
    status: 'idle',
    total_tests: 0,
    threats_detected: 0
  });
  
  const [latestThreat, setLatestThreat] = useState(null);
  const [testResults, setTestResults] = useState([]);

  // Simulate real-time updates (in production, use WebSocket)
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/sandbox/status');
        const data = await response.json();
        setSandboxStatus(data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const runAttackSimulation = async (attackType) => {
    try {
      const response = await fetch('/api/sandbox/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ attack_type: attackType })
      });
      
      const result = await response.json();
      setLatestThreat(result);
      setTestResults(prev => [result, ...prev].slice(0, 10));
    } catch (error) {
      console.error('Error running simulation:', error);
    }
  };

  const getThreatLevelColor = (level) => {
    const colors = {
      'CRITICAL': 'bg-red-600',
      'HIGH': 'bg-orange-500',
      'MEDIUM': 'bg-yellow-500',
      'LOW': 'bg-green-500'
    };
    return colors[level] || 'bg-gray-500';
  };

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Digital Twin Security Sandbox
        </h1>
        <p className="text-gray-600 mt-2">
          Real-time threat detection and analysis for Daimler automotive systems
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Sandbox Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">
                {sandboxStatus.status.toUpperCase()}
              </span>
              <Badge className={
                sandboxStatus.status === 'running' ? 'bg-blue-500' :
                sandboxStatus.status === 'threat_detected' ? 'bg-red-500' :
                'bg-green-500'
              }>
                {sandboxStatus.status}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Tests Run
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {sandboxStatus.total_tests}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Threats Detected
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {sandboxStatus.threats_detected}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Attack Simulation Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Run Attack Simulation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <button
              onClick={() => runAttackSimulation('replay_attack')}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Replay Attack
            </button>
            <button
              onClick={() => runAttackSimulation('fuzzing_attack')}
              className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
            >
              Fuzzing Attack
            </button>
            <button
              onClick={() => runAttackSimulation('dos_attack')}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              DoS Attack
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Latest Threat Analysis */}
      {latestThreat && (
        <Alert className={
          latestThreat.threat_detected ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'
        }>
          <AlertDescription>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-lg">
                  Latest Analysis: {latestThreat.attack_type}
                </h3>
                <Badge className={getThreatLevelColor(latestThreat.analysis.threat_level)}>
                  {latestThreat.analysis.threat_level}
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-semibold">Threat Detected:</span>{' '}
                  {latestThreat.threat_detected ? '🚨 YES' : '✓ NO'}
                </div>
                <div>
                  <span className="font-semibold">Confidence:</span>{' '}
                  {latestThreat.analysis.confidence.toFixed(2)}%
                </div>
                <div>
                  <span className="font-semibold">Identified As:</span>{' '}
                  {latestThreat.analysis.attack_type}
                </div>
                <div>
                  <span className="font-semibold">Anomaly Score:</span>{' '}
                  {latestThreat.analysis.anomaly_score.toFixed(4)}
                </div>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Test Results History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Test Results</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {testResults.map((result, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-white rounded border"
              >
                <div>
                  <span className="font-semibold">{result.attack_type}</span>
                  <span className="text-sm text-gray-600 ml-3">
                    {result.analysis.attack_type}
                  </span>
                </div>
                <Badge className={getThreatLevelColor(result.analysis.threat_level)}>
                  {result.analysis.threat_level}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ThreatMonitoringDashboard;
