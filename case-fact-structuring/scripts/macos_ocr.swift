import Foundation
import Vision
import AppKit
import PDFKit

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path)
var cg: CGImage?
if path.lowercased().hasSuffix(".pdf") {
    let index = CommandLine.arguments.count > 2 ? Int(CommandLine.arguments[2])! - 1 : 0
    if let document = PDFDocument(url: url), let page = document.page(at:index) {
        let rect = page.bounds(for:.mediaBox)
        let image = page.thumbnail(of:NSSize(width:1800,height:1800 * rect.height/rect.width),for:.mediaBox)
        var r = CGRect(origin:.zero,size:image.size)
        cg = image.cgImage(forProposedRect:&r,context:nil,hints:nil)
    }
} else if let image = NSImage(contentsOf:url) {
    var r = CGRect(origin:.zero,size:image.size)
    cg = image.cgImage(forProposedRect:&r,context:nil,hints:nil)
}
guard let image = cg else { fputs("无法解码图片或 PDF 页\n",stderr); exit(1) }
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans","en-US"]
request.usesLanguageCorrection = false
try VNImageRequestHandler(cgImage:image,options:[:]).perform([request])
let observations = (request.results ?? []).sorted {
    abs($0.boundingBox.midY - $1.boundingBox.midY) > 0.012
      ? $0.boundingBox.midY > $1.boundingBox.midY : $0.boundingBox.minX < $1.boundingBox.minX
}
let blocks:[[String:Any]] = observations.compactMap { o in
    guard let candidate = o.topCandidates(1).first else { return nil }
    let b = o.boundingBox
    return ["text":candidate.string,"box":[b.minX,b.minY,b.width,b.height],"confidence":candidate.confidence]
}
let result:[String:Any] = ["text":blocks.map{$0["text"] as! String}.joined(separator:"\n"),"blocks":blocks]
let encoded = try JSONSerialization.data(withJSONObject:result,options:[.sortedKeys])
print(String(data:encoded,encoding:.utf8)!)
