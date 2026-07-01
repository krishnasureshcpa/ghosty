import Cocoa
import SwiftUI

struct GhostyView: View {
    @State private var statusText = "Loading..."
    @State private var isGhostyAvailable = false

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "shield.checkered")
                .font(.system(size: 36))
                .foregroundStyle(.tint)
            Text("Ghosty Companion")
                .font(.title2.bold())

            ScrollView {
                Text(statusText)
                    .font(.body.monospaced())
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .textSelection(.enabled)
            }
            .frame(maxHeight: .infinity)
            .padding(8)
            .background(Color(nsColor: .textBackgroundColor))
            .cornerRadius(6)

            HStack(spacing: 12) {
                Button("Refresh") { runDoctor() }
                    .buttonStyle(.bordered)
                Button("Launch TUI") { launchGhosty() }
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .frame(width: 480, height: 400)
        .onAppear(perform: runDoctor)
    }

    private func runDoctor() {
        statusText = "Running ghosty doctor..."
        let output = shell("ghosty", "doctor", "--json")
        if output.isEmpty || output.contains("not found") {
            statusText = "⚠ ghosty CLI not found\n\nInstall: uv tool install ghosty-cli"
            isGhostyAvailable = false
        } else {
            statusText = output
            isGhostyAvailable = true
        }
    }

    private func launchGhosty() {
        _ = shell("open", "-a", "Terminal", "ghosty")
    }
}

@main
struct GhostyCompanionApp: App {
    var body: some Scene {
        WindowGroup {
            GhostyView()
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
        process.waitUntilExit()
        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        return String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
    } catch {
        return "error: \(error.localizedDescription)"
    }
}
