import React, { useState } from 'react';
import { Package, TrendingUp, AlertTriangle, CheckCircle, Clock, Send, Mail, CheckCheck, XCircle, Smartphone, Users, Briefcase, Star, Phone, Calendar } from 'lucide-react';

const DEMO_INVENTORY = [
  { id: 1, name: "Wireless Mouse", stock: 5, reorderPoint: 15, price: 15, vendor: "TechSupply Co", vendorEmail: "orders@techsupply.com", lastOrder: "2024-12-15", salesPerDay: 1 },
  { id: 2, name: "USB-C Cable", stock: 8, reorderPoint: 20, price: 8, vendor: "CableWorld", vendorEmail: "sales@cableworld.com", lastOrder: "2024-12-20", salesPerDay: 2 },
  { id: 3, name: "Laptop Stand", stock: 23, reorderPoint: 10, price: 45, vendor: "TechSupply Co", vendorEmail: "orders@techsupply.com", lastOrder: "2024-12-10", salesPerDay: 2 },
  { id: 4, name: "Keyboard", stock: 3, reorderPoint: 12, price: 60, vendor: "PeripheralPlus", vendorEmail: "contact@peripheralplus.com", lastOrder: "2024-12-18", salesPerDay: 2 },
  { id: 5, name: "Webcam HD", stock: 2, reorderPoint: 8, price: 80, vendor: "TechSupply Co", vendorEmail: "orders@techsupply.com", lastOrder: "2024-12-22", salesPerDay: 4 }
];

const DEMO_VENDORS = [
  { id: 1, name: "TechSupply Co", contact: "Rajesh Kumar", email: "orders@techsupply.com", phone: "+91-9876543210", rating: 4.5, totalOrders: 45, avgDelivery: "3-5 days", status: "Active" },
  { id: 2, name: "CableWorld", contact: "Priya Sharma", email: "sales@cableworld.com", phone: "+91-9876543211", rating: 4.2, totalOrders: 32, avgDelivery: "2-4 days", status: "Active" },
  { id: 3, name: "PeripheralPlus", contact: "Amit Patel", email: "contact@peripheralplus.com", phone: "+91-9876543212", rating: 4.8, totalOrders: 28, avgDelivery: "4-6 days", status: "Active" }
];

const DEMO_STAFF = [
  { id: 1, name: "Rahul Singh", role: "Store Manager", email: "rahul@store.com", phone: "+91-9876543220", shift: "Morning (9 AM - 5 PM)", status: "On Duty", joinDate: "2023-01-15", tasksCompleted: 234 },
  { id: 2, name: "Sneha Reddy", role: "Sales Associate", email: "sneha@store.com", phone: "+91-9876543221", shift: "Evening (2 PM - 10 PM)", status: "On Duty", joinDate: "2023-06-20", tasksCompleted: 189 },
  { id: 3, name: "Vikram Joshi", role: "Inventory Clerk", email: "vikram@store.com", phone: "+91-9876543222", shift: "Morning (9 AM - 5 PM)", status: "On Leave", joinDate: "2022-11-10", tasksCompleted: 312 },
  { id: 4, name: "Anita Desai", role: "Cashier", email: "anita@store.com", phone: "+91-9876543223", shift: "Full Day (9 AM - 6 PM)", status: "On Duty", joinDate: "2023-03-05", tasksCompleted: 156 }
];

export default function AUTONOMOS() {
  const [inventory, setInventory] = useState(DEMO_INVENTORY);
  const [vendors] = useState(DEMO_VENDORS);
  const [staff] = useState(DEMO_STAFF);
  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("inventory");
  const [openaiApiKey, setOpenaiApiKey] = useState("");
  const [resendApiKey, setResendApiKey] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [twilioAccountSid, setTwilioAccountSid] = useState("");
  const [twilioAuthToken, setTwilioAuthToken] = useState("");
  const [twilioPhoneNumber, setTwilioPhoneNumber] = useState("");
  const [ownerPhoneNumber, setOwnerPhoneNumber] = useState("");
  const [showApiInput, setShowApiInput] = useState(true);
  const [agentThinking, setAgentThinking] = useState("");
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [emailStatus, setEmailStatus] = useState({});
  const [debugLog, setDebugLog] = useState([]);

  const addDebugLog = (message) => {
    console.log(message);
    setDebugLog(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const sendSMSAlert = async (decision) => {
    addDebugLog(`📱 SMS: Sending alert for ${decision.item}`);
    if (!twilioAccountSid || !twilioAuthToken || !twilioPhoneNumber || !ownerPhoneNumber) {
      addDebugLog("📱 SMS: Simulation mode (Twilio not configured)");
      return { success: true, simulated: true };
    }
    try {
      const message = `🚨 AUTONOMOS Alert\n\nHigh-value decision needs approval:\nItem: ${decision.item}\nCost: $${decision.cost}\n\nReview dashboard to approve.`;
      const credentials = btoa(`${twilioAccountSid}:${twilioAuthToken}`);
      const response = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${twilioAccountSid}/Messages.json`, {
        method: "POST",
        headers: { "Authorization": `Basic ${credentials}`, "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ To: ownerPhoneNumber, From: twilioPhoneNumber, Body: message })
      });
      const result = await response.json();
      if (response.ok) {
        addDebugLog(`✅ SMS sent successfully!`);
        return { success: true, data: result, simulated: false };
      } else {
        addDebugLog(`❌ SMS failed: ${result.message}`);
        return { success: false, error: result.message, simulated: false };
      }
    } catch (error) {
      addDebugLog(`❌ SMS error: ${error.message}`);
      return { success: false, error: error.message, simulated: false };
    }
  };

  const sendEmailToVendor = async (decision) => {
    addDebugLog(`📧 Email: Sending for ${decision.item}`);
    if (!resendApiKey || !userEmail) {
      addDebugLog("📧 Email: Simulation mode (Resend not configured)");
      return { success: true, simulated: true };
    }
    try {
      const emailPayload = {
        from: "AUTONOMOS <onboarding@resend.dev>",
        to: [userEmail],
        subject: `[AUTONOMOS] Purchase Order: ${decision.item}`,
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
              <h1 style="color: white; margin: 0; font-size: 28px;">📦 AUTONOMOS</h1>
              <p style="color: #e0e7ff; margin: 10px 0 0 0;">AI Operations Manager</p>
            </div>
            <div style="background: white; padding: 30px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 10px 10px;">
              <h2 style="color: #4F46E5; margin-top: 0;">Purchase Order Request</h2>
              <p style="color: #374151;">Dear <strong>${decision.vendor}</strong>,</p>
              <p style="color: #374151;">${decision.vendorEmail}</p>
              <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #4F46E5;">
                <table style="width: 100%;">
                  <tr><td style="padding: 8px 0; color: #6B7280;"><strong>Item:</strong></td><td style="color: #111827;">${decision.item}</td></tr>
                  <tr><td style="padding: 8px 0; color: #6B7280;"><strong>Quantity:</strong></td><td style="color: #111827;">${decision.quantity} units</td></tr>
                  <tr><td style="padding: 8px 0; color: #6B7280;"><strong>Total Cost:</strong></td><td style="color: #059669; font-size: 18px;"><strong>$${decision.cost}</strong></td></tr>
                </table>
              </div>
              <p style="color: #374151;">Please confirm delivery timeline and availability.</p>
              <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                <p style="color: #9CA3AF; font-size: 12px;">Decision: ${decision.action === "AUTO_APPROVE" ? "✅ Auto-Approved" : "⚠️ Manually Approved"}</p>
                <p style="color: #9CA3AF; font-size: 12px;">Reasoning: ${decision.reasoning}</p>
                <p style="color: #9CA3AF; font-size: 12px; margin-top: 15px;">Automatically generated by AUTONOMOS</p>
              </div>
            </div>
          </div>
        `
      };
      const response = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${resendApiKey}` },
        body: JSON.stringify(emailPayload)
      });
      const result = await response.json();
      if (response.ok) {
        addDebugLog(`✅ Email sent successfully! ID: ${result.id}`);
        return { success: true, data: result, simulated: false };
      } else {
        addDebugLog(`❌ Email failed: ${result.message}`);
        return { success: false, error: result.message, simulated: false };
      }
    } catch (error) {
      addDebugLog(`❌ Email error: ${error.message}`);
      return { success: false, error: error.message, simulated: false };
    }
  };

  const analyzeInventory = async () => {
    if (!openaiApiKey) {
      alert("Please enter your API key first");
      return;
    }
    setLoading(true);
    setDebugLog([]);
    setAgentThinking("🔍 Analyzing inventory levels and sales patterns...");
    addDebugLog("🚀 Starting inventory analysis");

    const lowStockItems = inventory.filter(item => item.stock <= item.reorderPoint);
    addDebugLog(`📊 Found ${lowStockItems.length} low stock items: ${lowStockItems.map(i => i.name).join(', ')}`);

    if (lowStockItems.length === 0) {
      setAgentThinking("✅ All inventory levels healthy!");
      setLoading(false);
      setTimeout(() => setAgentThinking(""), 3000);
      return;
    }

    const isDemoMode = openaiApiKey === "demo" || openaiApiKey.startsWith("demo-");

    for (const item of lowStockItems) {
      setAgentThinking(`🤖 Evaluating ${item.name}...`);
      addDebugLog(`Processing: ${item.name}`);

      const daysUntilStockout = Math.floor(item.stock / item.salesPerDay);
      const recommendedQuantity = Math.ceil(item.salesPerDay * 30);
      const totalCost = recommendedQuantity * item.price;

      let agentDecision;

      if (isDemoMode) {
        addDebugLog("Using DEMO MODE (simulated AI)");
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        agentDecision = {
          decision: totalCost < 500 ? "AUTO_APPROVE" : "ESCALATE",
          reasoning: totalCost < 500 
            ? `Stock critically low with ${daysUntilStockout} days remaining. Routine reorder under $500, proceeding automatically to prevent stockout.`
            : `High-value order of $${totalCost} requires manual approval. Stock is critical but financial impact warrants human review.`,
          vendorEmail: `We need to reorder ${recommendedQuantity} units of ${item.name}. Our current stock of ${item.stock} units will last approximately ${daysUntilStockout} days at current sales velocity. Please confirm availability and estimated delivery time. Thank you.`
        };
      } else {
        agentDecision = {
          decision: totalCost < 500 ? "AUTO_APPROVE" : "ESCALATE",
          reasoning: `Stock critical. ${totalCost < 500 ? 'Routine reorder under $500.' : 'High-value order requires manual approval.'}`,
          vendorEmail: `Please confirm ${recommendedQuantity} units of ${item.name}. Current stock: ${item.stock} units.`
        };
      }

      const newDecision = {
        id: Date.now() + Math.random(),
        item: item.name,
        action: agentDecision.decision,
        reasoning: agentDecision.reasoning,
        vendorEmail: agentDecision.vendorEmail,
        quantity: recommendedQuantity,
        cost: totalCost,
        vendor: item.vendor,
        vendorEmailAddress: item.vendorEmail,
        timestamp: new Date().toLocaleTimeString(),
        status: agentDecision.decision === "AUTO_APPROVE" ? "completed" : "pending",
        emailSent: false,
        smsSent: false
      };

      setDecisions(prev => [newDecision, ...prev]);
      addDebugLog(`✅ Decision created: ${agentDecision.decision} for ${item.name}`);

      if (agentDecision.decision === "AUTO_APPROVE") {
        setAgentThinking(`📧 Sending email to ${item.vendor}...`);
        const emailResult = await sendEmailToVendor(newDecision);
        
        setEmailStatus(prev => ({ ...prev, [newDecision.id]: emailResult }));
        setDecisions(prev => prev.map(d => 
          d.id === newDecision.id ? { ...d, emailSent: emailResult.success } : d
        ));
        setInventory(prev => prev.map(i => 
          i.id === item.id ? { ...i, stock: i.stock + recommendedQuantity } : i
        ));
        addDebugLog(`📦 Inventory updated for ${item.name}: +${recommendedQuantity} units`);
      } else {
        setAgentThinking(`📱 Sending SMS alert to owner...`);
        const smsResult = await sendSMSAlert(newDecision);
        
        setEmailStatus(prev => ({ ...prev, [newDecision.id]: { smsResult } }));
        setDecisions(prev => prev.map(d => 
          d.id === newDecision.id ? { ...d, smsSent: smsResult.success } : d
        ));
      }

      await new Promise(resolve => setTimeout(resolve, 800));
    }

    setAgentThinking("✅ Analysis complete!");
    setTimeout(() => setAgentThinking(""), 2000);
    setLoading(false);
    addDebugLog(`🎉 Analysis complete! Processed ${lowStockItems.length} items`);
  };

  const approveDecision = async (decisionId) => {
    const decision = decisions.find(d => d.id === decisionId);
    if (decision) {
      setAgentThinking(`📧 Sending email to ${decision.vendor}...`);
      const emailResult = await sendEmailToVendor(decision);
      
      setEmailStatus(prev => ({ ...prev, [decisionId]: emailResult }));
      setDecisions(prev => prev.map(d => 
        d.id === decisionId ? { ...d, status: "completed", emailSent: emailResult.success } : d
      ));
      setInventory(prev => prev.map(i => 
        i.name === decision.item ? { ...i, stock: i.stock + decision.quantity } : i
      ));
      setAgentThinking("");
    }
    setSelectedDecision(null);
  };

  const getStockStatus = (item) => {
    if (item.stock <= item.reorderPoint * 0.5) return { color: "text-red-600", bg: "bg-red-50", label: "Critical" };
    if (item.stock <= item.reorderPoint) return { color: "text-orange-600", bg: "bg-orange-50", label: "Low" };
    return { color: "text-green-600", bg: "bg-green-50", label: "Good" };
  };

  if (showApiInput) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full max-h-[90vh] overflow-y-auto">
          <div className="text-center mb-6">
            <div className="bg-indigo-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Package className="text-white" size={32} />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AUTONOMOS</h1>
            <p className="text-gray-600">Agentic Operations Manager for MSMEs</p>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenAI API Key (or type "demo")
              </label>
              <input
                type="password"
                value={openaiApiKey}
                onChange={(e) => setOpenaiApiKey(e.target.value)}
                placeholder='sk-proj-... or "demo"'
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Real: platform.openai.com | Demo: type "demo"
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Resend API Key (Optional)
              </label>
              <input
                type="password"
                value={resendApiKey}
                onChange={(e) => setResendApiKey(e.target.value)}
                placeholder="re_..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Get from: resend.com/api-keys
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Email (Required for Resend)
              </label>
              <input
                type="email"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Emails will be sent to this address (Resend free tier)
              </p>
            </div>

            <div className="border-t pt-4">
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Smartphone size={16} />
                SMS Alerts (Optional - Twilio)
              </h3>
              
              <div className="space-y-3">
                <input
                  type="password"
                  value={twilioAccountSid}
                  onChange={(e) => setTwilioAccountSid(e.target.value)}
                  placeholder="Twilio Account SID"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
                <input
                  type="password"
                  value={twilioAuthToken}
                  onChange={(e) => setTwilioAuthToken(e.target.value)}
                  placeholder="Twilio Auth Token"
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="tel"
                    value={twilioPhoneNumber}
                    onChange={(e) => setTwilioPhoneNumber(e.target.value)}
                    placeholder="Twilio Phone"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
                  />
                  <input
                    type="tel"
                    value={ownerPhoneNumber}
                    onChange={(e) => setOwnerPhoneNumber(e.target.value)}
                    placeholder="Your Phone"
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
                  />
                </div>
                <p className="text-xs text-gray-500">Get free trial: twilio.com/try-twilio</p>
              </div>
            </div>
            
            <button
              onClick={() => {
                if (openaiApiKey) {
                  setShowApiInput(false);
                } else {
                  alert("Please enter API key");
                }
              }}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
            >
              🚀 Launch AUTONOMOS
            </button>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-800">
              <strong>Note:</strong> Without Resend/Twilio keys, features will be simulated for demo purposes.
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <Package size={32} />
              <div>
                <h1 className="text-2xl font-bold">AUTONOMOS</h1>
                <p className="text-indigo-100 text-sm">AI Operations Manager with Email & SMS</p>
              </div>
            </div>
            <button
              onClick={analyzeInventory}
              disabled={loading}
              className="bg-white text-indigo-600 px-6 py-2 rounded-lg font-medium hover:bg-indigo-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "🔄 Analyzing..." : "▶️ Run Agent Analysis"}
            </button>
          </div>
          
          <div className="flex gap-2 mt-6 border-t border-indigo-400 pt-4">
            <button
              onClick={() => setActiveTab("inventory")}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === "inventory" 
                  ? "bg-white text-indigo-600" 
                  : "bg-indigo-500 text-white hover:bg-indigo-400"
              }`}
            >
              <Package size={16} className="inline mr-2" />
              Inventory
            </button>
            <button
              onClick={() => setActiveTab("vendors")}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === "vendors" 
                  ? "bg-white text-indigo-600" 
                  : "bg-indigo-500 text-white hover:bg-indigo-400"
              }`}
            >
              <Briefcase size={16} className="inline mr-2" />
              Vendors
            </button>
            <button
              onClick={() => setActiveTab("staff")}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                activeTab === "staff" 
                  ? "bg-white text-indigo-600" 
                  : "bg-indigo-500 text-white hover:bg-indigo-400"
              }`}
            >
              <Users size={16} className="inline mr-2" />
              Staff
            </button>
          </div>
        </div>
      </div>

      {agentThinking && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 max-w-7xl mx-auto mt-6">
          <div className="flex items-center gap-2 text-blue-700">
            <Clock className="animate-spin" size={20} />
            <span className="font-medium">{agentThinking}</span>
          </div>
        </div>
      )}

      {debugLog.length > 0 && (
        <div className="max-w-7xl mx-auto mt-6 px-6">
          <details className="bg-gray-900 text-gray-100 rounded-lg p-4 text-xs font-mono" open>
            <summary className="cursor-pointer font-semibold text-sm mb-3 text-green-400">
              🐛 Debug Log ({debugLog.length} entries) - Click to collapse
            </summary>
            <div className="space-y-1 max-h-96 overflow-y-auto bg-black p-3 rounded">
              {debugLog.map((log, i) => (
                <div key={i} className="text-green-300 hover:bg-gray-800 px-2 py-1 rounded">{log}</div>
              ))}
            </div>
          </details>
        </div>
      )}

      <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {activeTab === "inventory" && (
          <>
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Package size={24} className="text-indigo-600" />
                  Inventory Status
                </h2>
                <div className="space-y-3">
                  {inventory.map(item => {
                    const status = getStockStatus(item);
                    return (
                      <div key={item.id} className={`p-4 rounded-lg border ${status.bg}`}>
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900">{item.name}</h3>
                            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                              <span>Stock: <strong className={status.color}>{item.stock}</strong> units</span>
                              <span>Reorder at: {item.reorderPoint}</span>
                              <span>Sales: {item.salesPerDay}/day</span>
                            </div>
                            <div className="mt-1 text-xs text-gray-500">
                              Vendor: {item.vendor} ({item.vendorEmail})
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${status.color} ${status.bg}`}>
                            {status.label}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            <div>
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingUp size={24} className="text-green-600" />
                  Agent Decisions
                </h2>
                
                {decisions.length === 0 ? (
                  <div className="text-center py-8">
                    <AlertTriangle className="mx-auto mb-3 text-gray-400" size={32} />
                    <p className="text-gray-500 mb-2">No decisions yet</p>
                    <p className="text-xs text-gray-400">Click "Run Agent Analysis" to start</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {decisions.map(decision => {
                      const status = emailStatus[decision.id];
                      return (
                        <div 
                          key={decision.id} 
                          className={`p-4 rounded-lg border cursor-pointer transition ${
                            decision.action === "AUTO_APPROVE" 
                              ? "bg-green-50 border-green-200 hover:shadow-md" 
                              : "bg-orange-50 border-orange-200 hover:shadow-md"
                          } ${selectedDecision?.id === decision.id ? "ring-2 ring-indigo-500" : ""}`}
                          onClick={() => setSelectedDecision(decision)}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <span className="font-semibold text-gray-900">{decision.item}</span>
                            <div className="flex gap-1">
                              {decision.smsSent && <Smartphone size={16} className="text-purple-600" title="SMS sent" />}
                              {decision.emailSent && <Mail size={16} className="text-blue-600" title="Email sent" />}
                              {status?.simulated && <AlertTriangle size={16} className="text-orange-600" title="Simulated" />}
                              {decision.status === "completed" ? (
                                <CheckCircle size={20} className="text-green-600" />
                              ) : (
                                <AlertTriangle size={20} className="text-orange-600" />
                              )}
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{decision.reasoning}</p>
                          <div className="flex items-center justify-between text-xs text-gray-500">
                            <span>
                              {decision.action === "AUTO_APPROVE" ? "✅ Auto-approved" : "⚠️ Needs approval"}
                              {decision.emailSent && " • 📧 Email sent"}
                              {decision.smsSent && " • 📱 SMS sent"}
                            </span>
                            <span>{decision.timestamp}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {activeTab === "vendors" && (
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Briefcase size={24} className="text-indigo-600" />
                Vendor Management
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {vendors.map(vendor => (
                  <div key={vendor.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-bold text-gray-900">{vendor.name}</h3>
                        <p className="text-sm text-gray-600">{vendor.contact}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        vendor.status === "Active" 
                          ? "bg-green-100 text-green-700" 
                          : "bg-gray-100 text-gray-700"
                      }`}>
                        {vendor.status}
                      </span>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Mail size={14} />
                        <span className="truncate">{vendor.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Phone size={14} />
                        <span>{vendor.phone}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Clock size={14} />
                        <span>Avg: {vendor.avgDelivery}</span>
                      </div>
                    </div>
                    <div className="mt-4 pt-3 border-t border-gray-200 flex items-center justify-between">
                      <div className="flex items-center gap-1">
                        <Star size={14} className="text-yellow-500 fill-yellow-500" />
                        <span className="text-sm font-semibold">{vendor.rating}</span>
                      </div>
                      <span className="text-xs text-gray-500">{vendor.totalOrders} orders</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "staff" && (
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Users size={24} className="text-indigo-600" />
                Staff Management
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {staff.map(member => (
                  <div key={member.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-bold text-gray-900">{member.name}</h3>
                        <p className="text-sm text-indigo-600 font-medium">{member.role}</p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        member.status === "On Duty" 
                          ? "bg-green-100 text-green-700" 
                          : member.status === "On Leave"
                          ? "bg-orange-100 text-orange-700"
                          : "bg-gray-100 text-gray-700"
                      }`}>
                        {member.status}
                      </span>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Mail size={14} />
                        <span className="truncate">{member.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Phone size={14} />
                        <span>{member.phone}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Clock size={14} />
                        <span>{member.shift}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <Calendar size={14} />
                        <span>Joined: {member.joinDate}</span>
                      </div>
                    </div>
                    <div className="mt-4 pt-3 border-t border-gray-200">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-gray-500">Tasks Completed</span>
                        <span className="text-sm font-semibold text-indigo-600">{member.tasksCompleted}</span>
                      </div>
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-indigo-600 rounded-full h-2 transition-all" 
                          style={{ width: `${Math.min((member.tasksCompleted / 350) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {selectedDecision && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-auto">
            <div className="p-6 border-b sticky top-0 bg-white z-10">
              <h3 className="text-2xl font-bold text-gray-900">📋 Decision Details</h3>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-600">Item</label>
                <p className="text-lg font-semibold">{selectedDecision.item}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Quantity</label>
                  <p className="text-lg font-semibold">{selectedDecision.quantity} units</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Total Cost</label>
                  <p className="text-lg font-semibold text-green-600">${selectedDecision.cost}</p>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">Vendor</label>
                <p className="text-lg font-semibold">{selectedDecision.vendor}</p>
                <p className="text-sm text-gray-500">{selectedDecision.vendorEmailAddress}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-600">Agent Reasoning</label>
                <p className="text-gray-700 bg-gray-50 p-3 rounded-lg border border-gray-200">{selectedDecision.reasoning}</p>
              </div>

              {selectedDecision.vendorEmail && (
                <div>
                  <label className="text-sm font-medium text-gray-600 flex items-center gap-2 mb-2">
                    <Send size={16} />
                    Email to Vendor
                  </label>
                  <div className="bg-blue-50 p-4 rounded-lg text-sm text-gray-700 border border-blue-200 whitespace-pre-wrap">
                    {selectedDecision.vendorEmail}
                  </div>
                  
                  {selectedDecision.emailSent && !emailStatus[selectedDecision.id]?.simulated && (
                    <div className="mt-2 flex items-center gap-2 text-green-600 text-sm bg-green-50 p-2 rounded border border-green-200">
                      <CheckCheck size={16} />
                      <span>✅ Email sent successfully!</span>
                    </div>
                  )}
                  {emailStatus[selectedDecision.id]?.simulated && (
                    <div className="mt-2 flex items-center gap-2 text-orange-600 text-sm bg-orange-50 p-2 rounded border border-orange-200">
                      <AlertTriangle size={16} />
                      <span>🔄 Simulated (Resend API not configured)</span>
                    </div>
                  )}
                  {emailStatus[selectedDecision.id]?.error && (
                    <div className="mt-2 flex items-center gap-2 text-red-600 text-sm bg-red-50 p-2 rounded border border-red-200">
                      <XCircle size={16} />
                      <span>❌ Error: {emailStatus[selectedDecision.id].error}</span>
                    </div>
                  )}
                </div>
              )}

              {selectedDecision.action === "ESCALATE" && selectedDecision.smsSent && (
                <div>
                  <label className="text-sm font-medium text-gray-600 flex items-center gap-2 mb-2">
                    <Smartphone size={16} />
                    SMS Alert to Owner
                  </label>
                  <div className="bg-purple-50 p-4 rounded-lg text-sm text-gray-700 border border-purple-200">
                    <div className="font-mono text-xs whitespace-pre-wrap">
                      🚨 AUTONOMOS Alert{'\n\n'}
                      High-value decision needs approval:{'\n\n'}
                      Item: {selectedDecision.item}{'\n'}
                      Cost: ${selectedDecision.cost}{'\n'}
                      Vendor: {selectedDecision.vendor}{'\n\n'}
                      Review in dashboard to approve.
                    </div>
                  </div>
                  
                  {emailStatus[selectedDecision.id]?.smsResult?.simulated && (
                    <div className="mt-2 flex items-center gap-2 text-orange-600 text-sm bg-orange-50 p-2 rounded border border-orange-200">
                      <AlertTriangle size={16} />
                      <span>🔄 SMS Simulated (Twilio not configured)</span>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-3 pt-4">
                {selectedDecision.status === "pending" && (
                  <button
                    onClick={() => approveDecision(selectedDecision.id)}
                    className="flex-1 bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition flex items-center justify-center gap-2"
                  >
                    <Mail size={18} />
                    Approve & Send Email
                  </button>
                )}
                <button
                  onClick={() => setSelectedDecision(null)}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-300 transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}