// swift-tools-version: 6.1
import PackageDescription

let package = Package(
    name: "GhostyCompanion",
    platforms: [.macOS(.v15)],
    targets: [
        .executableTarget(
            name: "GhostyCompanion"
        ),
    ]
)
