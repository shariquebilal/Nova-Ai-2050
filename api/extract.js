export default function handler(req, res) {
    // Frontend se bheji gayi link ko pakadna
    const videoUrl = req.query.url;

    if (!videoUrl) {
        return res.status(400).json({ success: false, message: "Bhai, link toh bhejo!" });
    }

    // Backend par securely Video ID nikalna
    let videoId = "";
    if (videoUrl.includes("shorts/")) videoId = videoUrl.split("shorts/")[1].split("?")[0];
    else if (videoUrl.includes("v=")) videoId = videoUrl.split("v=")[1].split("&")[0];
    else if (videoUrl.includes("youtu.be/")) videoId = videoUrl.split("youtu.be/")[1].split("?")[0];

    if (!videoId) {
        return res.status(400).json({ success: false, message: "Invalid YouTube Link! Sahi link daalo." });
    }

    // Success response aur download APIs ko wapas frontend bhejna
    res.status(200).json({
        success: true,
        message: "Server Processed Video Successfully! 🚀",
        videoId: videoId,
        // Hum 2 alag-alag download servers bhej rahe hain taaki ek fail ho toh dusra chale
        download_server_1: `https://api.vevioz.com/@api/button/mp4/${videoId}`,
        download_server_2: `https://loader.to/api/button/?url=https://www.youtube.com/watch?v=${videoId}&f=720`
    });
}
