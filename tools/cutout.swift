// Lift the main subject off its background with Apple Vision (a mask, nothing generated).
// swift tools/cutout.swift in.jpg out.png
import Foundation
import Vision
import CoreImage
import AppKit

let a = CommandLine.arguments
guard a.count == 3, let src = CIImage(contentsOf: URL(fileURLWithPath: a[1]), options: [.applyOrientationProperty: true]) else {
    FileHandle.standardError.write("usage: cutout.swift in out.png\n".data(using: .utf8)!); exit(2)
}
let req = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: src)
try handler.perform([req])
guard let obs = req.results?.first else { FileHandle.standardError.write("no subject found\n".data(using: .utf8)!); exit(1) }
let buf = try obs.generateMaskedImage(ofInstances: obs.allInstances, from: handler, croppedToInstancesExtent: false)
let out = CIImage(cvPixelBuffer: buf)
let ctx = CIContext()
try ctx.writePNGRepresentation(of: out, to: URL(fileURLWithPath: a[2]), format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
print("wrote \(a[2]) \(Int(out.extent.width))x\(Int(out.extent.height)) instances=\(obs.allInstances.count)")
