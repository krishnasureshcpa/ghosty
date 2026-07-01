import SwiftUI

public struct ContentView: View {
    @State private var statusLines: [(String, String)] = []
    @State private var isLoading = true
    @State private var ghostyAvailable = false

    public var body: some View {
        VStack(spacing: 16) {
            HStack {
                Image(systemName: "shield.checkered")
                    .font(.largeTitle)
                    .foregroundStyle(.tint)
                Text("Ghosty Companion")
                    .font(.title)
                    .bold()
            }
            .padding(.top)

            if isLoading {
                ProgressView("Running ghosty doctor...")
            } else if !ghostyAvailable {
                VStack(spacing: 12) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                    Text("ghosty CLI not found")
                    Text("Install with: uv tool install ghosty-cli")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding()
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Security Status")
                        .font(.headline)
                    ForEach(statusLines, id: \.0) { key, val in
                        HStack {
                            Text(key)
                                .foregroundStyle(.secondary)
                                .frame(width: 120, alignment: .trailing)
                            Text(val)
                                .font(.body.monospaced())
                                .foregroundStyle(val.contains("✓") || val.contains("enabled") || val.contains("pass") ? .green : .red)
                        }
                    }
                }
                .padding()
                .background(Color(nsColor: .windowBackgroundColor))
                .cornerRadius(8)
            }

            HStack(spacing: 16) {
                Button("Refresh Status") {
                    refreshStatus()
                }
                .buttonStyle(.bordered)

                Button("Launch TUI") {
                    launchTUI()
                }
                .buttonStyle(.borderedProminent)
            }
            .padding(.bottom)
        }
        .padding()
        .frame(width: 420, height: 360)
        .onAppear(perform: refreshStatus)
    }

    public init() {}

    nonisolated private func refreshStatus() {
        Task { @MainActor in
            isLoading = true
            let result = shell("ghosty", "doctor", "--json")
            if let data = result.data(using: .utf8),
               let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
            {
                ghostyAvailable = true
                statusLines = json.compactMap { key, value in
                    (key, "\(value)")
                }.sorted { $0.0 < $1.0 }
            } else if result.contains("error") || result.contains("not found") || result.isEmpty {
                ghostyAvailable = false
            } else {
                ghostyAvailable = true
                statusLines = [("raw", result.trimmingCharacters(in: .whitespacesAndNewlines))]
            }
            isLoading = false
        }
    }

    nonisolated private func launchTUI() {
        Task { @MainActor in
            shell("open", "-a", "Terminal", "ghosty")
        }
    }
}

private func shell(_ args: String...) -> String {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    process.arguments = args
    let pipe = Pipe()
    process.standardOutput = pipe
    process.standardError = pipe
    do {
        try process.run()
        process.waitUntilRunning()
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        return String(data: data, encoding: .utf8) ?? ""
    } catch {
        return "error: \(error.localizedDescription)"
    }
}
