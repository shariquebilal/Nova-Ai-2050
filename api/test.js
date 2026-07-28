export default function handler(req, res) {
    res.status(200).json({ 
        status: "Success", 
        message: "Bhai! NOVA AI ka Backend Engine 100% Zinda Hai! 🚀",
        server_time: new Date().toISOString()
    });
}
