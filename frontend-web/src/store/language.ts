import { create } from "zustand";
import { persist } from "zustand/middleware";
import { offlineWords } from "./offlineTranslations";

export type AppLanguage = "en" | "hi" | "mr";

interface LanguageState {
  language: AppLanguage;
  setLanguage: (language: AppLanguage) => void;
}
export const useLanguageStore = create<LanguageState>()(
  persist(
    (set) => ({
      language: "en",
      setLanguage: (language) => set({ language }),
    }),
    { name: "panchayat-language" },
  ),
);

export const words: Record<string, Record<AppLanguage, string>> = {
  Home: { en: "Home", hi: "होम", mr: "मुख्यपृष्ठ" },
  Assistant: { en: "Assistant", hi: "सहायक", mr: "सहाय्यक" },
  Help: { en: "Help", hi: "शिकायतें", mr: "तक्रारी" },
  Dues: { en: "Dues", hi: "बकाया", mr: "देयके" },
  Notices: { en: "Notices", hi: "सूचनाएं", mr: "सूचना" },
  Gate: { en: "Gate", hi: "गेट", mr: "प्रवेशद्वार" },
  People: { en: "People", hi: "लोग", mr: "लोक" },
  Admin: { en: "Admin", hi: "प्रशासन", mr: "प्रशासन" },
  Connected: { en: "Connected", hi: "कनेक्टेड", mr: "जोडलेले" },
  "Ask Panchayat": {
    en: "Ask Panchayat",
    hi: "पंचायत से पूछें",
    mr: "पंचायतीला विचारा",
  },
  "Speak or type. Panchayat can check records and complete approved tasks for you.":
    {
      en: "Speak or type. Panchayat can check records and complete approved tasks for you.",
      hi: "बोलें या लिखें। पंचायत रिकॉर्ड देखकर आपके लिए स्वीकृत काम पूरा कर सकती है।",
      mr: "बोला किंवा लिहा. पंचायत नोंदी तपासून तुमच्यासाठी मंजूर कामे पूर्ण करू शकते.",
    },
  "Your society dues": {
    en: "Your society dues",
    hi: "आपका सोसायटी बकाया",
    mr: "तुमची सोसायटी देयके",
  },
  "Monthly billing": {
    en: "Monthly billing",
    hi: "मासिक बिलिंग",
    mr: "मासिक बिलिंग",
  },
  "Notice Board": { en: "Notice Board", hi: "सूचना पट्ट", mr: "सूचना फलक" },
  "Admin Console": {
    en: "Admin Console",
    hi: "प्रशासन केंद्र",
    mr: "प्रशासन केंद्र",
  },
  "Pay all dues": {
    en: "Pay all dues",
    hi: "सभी बकाया भरें",
    mr: "सर्व देयके भरा",
  },
  "Demo payment": { en: "Demo payment", hi: "डेमो भुगतान", mr: "डेमो पेमेंट" },
  "Create monthly maintenance": {
    en: "Create monthly maintenance",
    hi: "मासिक रखरखाव बनाएं",
    mr: "मासिक देखभाल तयार करा",
  },
  "New notice": { en: "New notice", hi: "नई सूचना", mr: "नवीन सूचना" },
  "Sign out": { en: "Sign out", hi: "साइन आउट", mr: "साइन आउट" },
  "Say it. We’ll help get it done.": {
    en: "Say it. We’ll help get it done.",
    hi: "बस बताइए। हम काम पूरा करने में मदद करेंगे।",
    mr: "फक्त सांगा. आम्ही काम पूर्ण करण्यात मदत करू.",
  },
  "What would you like the Panchayat to do?": {
    en: "What would you like the Panchayat to do?",
    hi: "आप पंचायत से क्या करवाना चाहते हैं?",
    mr: "पंचायतीने तुमच्यासाठी काय करावे?",
  },
  "I prefer typing": {
    en: "I prefer typing",
    hi: "मैं लिखना चाहता हूँ",
    mr: "मी लिहिणे पसंत करतो",
  },
  "Active complaints": {
    en: "Active complaints",
    hi: "सक्रिय शिकायतें",
    mr: "सक्रिय तक्रारी",
  },
  "Maintenance due": {
    en: "Maintenance due",
    hi: "रखरखाव बकाया",
    mr: "देखभाल देय",
  },
  "Visitors inside": {
    en: "Visitors inside",
    hi: "अंदर आए मेहमान",
    mr: "आतील पाहुणे",
  },
  "Prefer doing it yourself?": {
    en: "Prefer doing it yourself?",
    hi: "खुद करना चाहते हैं?",
    mr: "स्वतः करायचे आहे?",
  },
  "Report a problem": {
    en: "Report a problem",
    hi: "समस्या दर्ज करें",
    mr: "समस्या नोंदवा",
  },
  "Check bills": { en: "Check bills", hi: "बकाया देखें", mr: "देयके पहा" },
  "Allow a visitor": {
    en: "Allow a visitor",
    hi: "मेहमान को अनुमति दें",
    mr: "पाहुण्याला परवानगी द्या",
  },
  "Read notices": { en: "Read notices", hi: "सूचनाएं पढ़ें", mr: "सूचना वाचा" },
  "Total to pay": { en: "Total to pay", hi: "कुल भुगतान", mr: "एकूण देय" },
  "Unpaid months": { en: "Unpaid months", hi: "बकाया महीने", mr: "थकीत महिने" },
  "Paid bills": { en: "Paid bills", hi: "भुगतान किए बिल", mr: "भरलेली देयके" },
  "Combined outstanding": {
    en: "Combined outstanding",
    hi: "कुल बकाया",
    mr: "एकत्रित थकबाकी",
  },
  "Months included": {
    en: "Months included",
    hi: "शामिल महीने",
    mr: "समाविष्ट महिने",
  },
  "Payment history": {
    en: "Payment history",
    hi: "भुगतान इतिहास",
    mr: "पेमेंट इतिहास",
  },
  "Know who is at the gate": {
    en: "Know who is at the gate",
    hi: "जानें गेट पर कौन है",
    mr: "प्रवेशद्वारावर कोण आहे ते पहा",
  },
  "Create gate pass": {
    en: "Create gate pass",
    hi: "गेट पास बनाएं",
    mr: "गेट पास तयार करा",
  },
  "Inside now": { en: "Inside now", hi: "अभी अंदर", mr: "सध्या आत" },
  "Awaiting approval": {
    en: "Awaiting approval",
    hi: "स्वीकृति की प्रतीक्षा",
    mr: "मंजुरीची प्रतीक्षा",
  },
  "Your community, clearly organized": {
    en: "Your community, clearly organized",
    hi: "आपका समुदाय, स्पष्ट रूप से व्यवस्थित",
    mr: "तुमचा समुदाय, स्पष्टपणे आयोजित",
  },
  Residents: { en: "Residents", hi: "निवासी", mr: "रहिवासी" },
  Committee: { en: "Committee", hi: "समिति", mr: "समिती" },
  Security: { en: "Security", hi: "सुरक्षा", mr: "सुरक्षा" },
  Administrators: { en: "Administrators", hi: "प्रशासक", mr: "प्रशासक" },
  "Complaint control room": {
    en: "Complaint control room",
    hi: "शिकायत नियंत्रण कक्ष",
    mr: "तक्रार नियंत्रण कक्ष",
  },
  "Problems, clearly tracked": {
    en: "Problems, clearly tracked",
    hi: "समस्याओं की स्पष्ट जानकारी",
    mr: "समस्यांचा स्पष्ट मागोवा",
  },
  "Tell the assistant": {
    en: "Tell the assistant",
    hi: "सहायक को बताएं",
    mr: "सहाय्यकाला सांगा",
  },
  Active: { en: "Active", hi: "सक्रिय", mr: "सक्रिय" },
  History: { en: "History", hi: "इतिहास", mr: "इतिहास" },
  "Request to join": {
    en: "Request to join",
    hi: "जुड़ने का अनुरोध",
    mr: "सामील होण्याची विनंती",
  },
  "Full name": { en: "Full name", hi: "पूरा नाम", mr: "पूर्ण नाव" },
  "Date of birth": { en: "Date of birth", hi: "जन्म तिथि", mr: "जन्मतारीख" },
  Society: { en: "Society", hi: "सोसायटी", mr: "सोसायटी" },
  Building: { en: "Building", hi: "इमारत", mr: "इमारत" },
  "Flat number": { en: "Flat number", hi: "फ्लैट नंबर", mr: "फ्लॅट क्रमांक" },
  Email: { en: "Email", hi: "ईमेल", mr: "ईमेल" },
  "Phone number": { en: "Phone number", hi: "फोन नंबर", mr: "फोन नंबर" },
  "COMMUNITY DESK": {
    en: "COMMUNITY DESK",
    hi: "सामुदायिक सेवा",
    mr: "समुदाय सेवा",
  },
  "IMPORTANT NOTICE": {
    en: "IMPORTANT NOTICE",
    hi: "महत्वपूर्ण सूचना",
    mr: "महत्त्वाची सूचना",
  },
  "View notice": { en: "View notice", hi: "सूचना देखें", mr: "सूचना पहा" },
  "Read important notice aloud": {
    en: "Read important notice aloud",
    hi: "महत्वपूर्ण सूचना सुनें",
    mr: "महत्त्वाची सूचना ऐका",
  },
  "Private • Permission checked": {
    en: "Private • Permission checked",
    hi: "निजी • अनुमति जांची गई",
    mr: "खाजगी • परवानगी तपासली",
  },
  "No forms. No department names. Explain the problem in Hindi, Marathi, Gujarati, or English.":
    {
      en: "No forms. No department names. Explain the problem in Hindi, Marathi, Gujarati, or English.",
      hi: "कोई फॉर्म नहीं। बस हिंदी, मराठी, गुजराती या अंग्रेजी में समस्या बताएं।",
      mr: "फॉर्मची गरज नाही. हिंदी, मराठी, गुजराती किंवा इंग्रजीत समस्या सांगा.",
    },
  "Start talking to Panchayat": {
    en: "Start talking to Panchayat",
    hi: "पंचायत से बोलें",
    mr: "पंचायतीशी बोला",
  },
  Speak: { en: "Speak", hi: "बोलें", mr: "बोला" },
  "Talk to a person": {
    en: "Talk to a person",
    hi: "किसी व्यक्ति से बात करें",
    mr: "व्यक्तीशी बोला",
  },
  "STAY INFORMED": {
    en: "STAY INFORMED",
    hi: "जानकारी रखें",
    mr: "माहिती मिळवा",
  },
  "All official updates in one place": {
    en: "All official updates in one place",
    hi: "सभी आधिकारिक सूचनाएं एक जगह",
    mr: "सर्व अधिकृत सूचना एकाच ठिकाणी",
  },
  "See all notices": {
    en: "See all notices",
    hi: "सभी सूचनाएं देखें",
    mr: "सर्व सूचना पहा",
  },
  "MANUAL SERVICES": {
    en: "MANUAL SERVICES",
    hi: "मैनुअल सेवाएं",
    mr: "मॅन्युअल सेवा",
  },
  "Every AI action has a manual fallback.": {
    en: "Every AI action has a manual fallback.",
    hi: "हर AI काम का मैनुअल विकल्प उपलब्ध है।",
    mr: "प्रत्येक AI कामासाठी मॅन्युअल पर्याय उपलब्ध आहे.",
  },
  "Water, road, light, waste, or safety": {
    en: "Water, road, light, waste, or safety",
    hi: "पानी, सड़क, बिजली, कचरा या सुरक्षा",
    mr: "पाणी, रस्ता, वीज, कचरा किंवा सुरक्षा",
  },
  "See dues, dates, and receipts": {
    en: "See dues, dates, and receipts",
    hi: "बकाया, तारीख और रसीद देखें",
    mr: "देयके, तारखा आणि पावत्या पहा",
  },
  "Create or cancel gate access": {
    en: "Create or cancel gate access",
    hi: "गेट अनुमति बनाएं या रद्द करें",
    mr: "गेट परवानगी तयार करा किंवा रद्द करा",
  },
  "Official source and simple explanation": {
    en: "Official source and simple explanation",
    hi: "आधिकारिक सूचना और सरल जानकारी",
    mr: "अधिकृत सूचना आणि सोपे स्पष्टीकरण",
  },
};

Object.assign(words, offlineWords);
const caseInsensitiveWords = new Map(
  Object.keys(words).map((key) => [key.toLocaleLowerCase("en-IN"), key]),
);

const societyPhrases: Array<[string, string, string]> = [
  ["bedroom roof se pani leakage", "बेडरूम की छत से पानी का रिसाव", "बेडरूमच्या छतामधून पाण्याची गळती"],
  ["bedroom ke roof se pani ka leak ho raha hai", "बेडरूम की छत से पानी रिस रहा है", "बेडरूमच्या छतामधून पाणी गळत आहे"],
  ["problem aaj (today) se start hui hai", "समस्या आज से शुरू हुई है", "समस्या आजपासून सुरू झाली आहे"],
  ["kripya urgent inspection aur repair karwaya jaye taaki property ko nuksan na ho", "कृपया तुरंत जाँच और मरम्मत कराएं ताकि संपत्ति को नुकसान न हो", "मालमत्तेचे नुकसान टाळण्यासाठी कृपया तातडीने तपासणी आणि दुरुस्ती करा"],
  ["request for repair of road potholes due to safety hazard and injury", "सुरक्षा खतरे और चोट के कारण सड़क के गड्ढों की मरम्मत का अनुरोध", "सुरक्षेचा धोका आणि दुखापत झाल्यामुळे रस्त्यावरील खड्डे दुरुस्त करण्याची विनंती"],
  ["many potholes are present on the road in", "सड़क पर कई गड्ढे हैं, स्थान", "रस्त्यावर अनेक खड्डे आहेत, ठिकाण"],
  ["this condition has been ongoing for the last two years", "यह स्थिति पिछले दो वर्षों से बनी हुई है", "ही परिस्थिती मागील दोन वर्षांपासून सुरू आहे"],
  ["the potholes have caused a safety hazard and i personally fell off my bike due to the potholes", "गड्ढों से सुरक्षा का खतरा पैदा हुआ है और मैं स्वयं बाइक से गिर गया", "खड्ड्यांमुळे सुरक्षेचा धोका निर्माण झाला असून मी स्वतः दुचाकीवरून पडलो"],
  ["request the society to inspect the road and carry out urgent patch repair/repair of the affected area to prevent further accidents", "आगे की दुर्घटनाएँ रोकने के लिए सोसायटी से सड़क का निरीक्षण और प्रभावित हिस्से की तत्काल मरम्मत का अनुरोध है", "पुढील अपघात टाळण्यासाठी सोसायटीने रस्त्याची तपासणी करून बाधित भागाची तातडीने दुरुस्ती करावी"],
  ["water leakage", "पानी का रिसाव", "पाण्याची गळती"],
  ["water supply", "पानी की आपूर्ति", "पाणीपुरवठा"],
  ["for the last two hours", "पिछले दो घंटों से", "मागील दोन तासांपासून"],
  ["disruption", "बाधा", "खंडित सेवा"],
  ["block", "ब्लॉक", "विंग"],
  ["not working", "काम नहीं कर रहा", "काम करत नाही"],
  ["since morning", "सुबह से", "सकाळपासून"],
  ["urgent repair", "तत्काल मरम्मत", "तातडीची दुरुस्ती"],
  ["road potholes", "सड़क के गड्ढे", "रस्त्यावरील खड्डे"],
  ["safety hazard", "सुरक्षा का खतरा", "सुरक्षेचा धोका"],
  ["garbage not collected", "कचरा नहीं उठाया गया", "कचरा उचललेला नाही"],
  ["street light", "सड़क की बत्ती", "रस्त्यावरील दिवा"],
  ["parking issue", "पार्किंग की समस्या", "पार्किंगची समस्या"],
  ["noise complaint", "शोर की शिकायत", "आवाजाची तक्रार"],
];

const societyContentMarker = /[\u0900-\u097f]|\b(leak|leakage|pani|water|pipe|sink|roof|lift|pothole|road|repair|garbage|waste|light|electric|parking|noise|security|safety|injury|complaint|problem|disruption|block)\b/i;

const societyWords: Record<string, [string, string]> = {
  a: ["एक", "एक"], an: ["एक", "एक"], the: ["", ""], and: ["और", "आणि"], or: ["या", "किंवा"],
  is: ["है", "आहे"], are: ["हैं", "आहेत"], was: ["था", "होता"], were: ["थे", "होते"], has: ["है", "आहे"], have: ["है", "आहे"],
  in: ["में", "मध्ये"], on: ["पर", "वर"], at: ["पर", "येथे"], from: ["से", "पासून"], for: ["के लिए", "साठी"], to: ["को", "ला"], of: ["का", "चा"],
  this: ["यह", "ही"], that: ["वह", "ती"], my: ["मेरे", "माझ्या"], our: ["हमारे", "आमच्या"], near: ["पास", "जवळ"],
  since: ["से", "पासून"], last: ["पिछले", "मागील"], past: ["पिछले", "मागील"], today: ["आज", "आज"], yesterday: ["कल", "काल"],
  hour: ["घंटा", "तास"], hours: ["घंटे", "तास"], day: ["दिन", "दिवस"], days: ["दिन", "दिवस"], week: ["सप्ताह", "आठवडा"], weeks: ["सप्ताह", "आठवडे"], month: ["महीना", "महिना"], months: ["महीने", "महिने"], year: ["वर्ष", "वर्ष"], years: ["वर्षों", "वर्षां"],
  morning: ["सुबह", "सकाळ"], evening: ["शाम", "संध्याकाळ"], night: ["रात", "रात्र"], continuously: ["लगातार", "सतत"],
  water: ["पानी", "पाणी"], supply: ["आपूर्ति", "पुरवठा"], disruption: ["बाधा", "खंडित सेवा"], leakage: ["रिसाव", "गळती"], leak: ["रिसाव", "गळती"], leaking: ["रिस रहा", "गळत आहे"],
  pipe: ["पाइप", "पाईप"], tap: ["नल", "नळ"], drain: ["नाली", "नाला"], bathroom: ["स्नानघर", "स्नानगृह"], bedroom: ["शयनकक्ष", "शयनकक्ष"], kitchen: ["रसोई", "स्वयंपाकघर"], toilet: ["शौचालय", "शौचालय"],
  roof: ["छत", "छत"], ceiling: ["छत", "छत"], wall: ["दीवार", "भिंत"], walls: ["दीवारें", "भिंती"], floor: ["मंजिल", "मजला"], flat: ["फ्लैट", "फ्लॅट"], wing: ["विंग", "विंग"], block: ["ब्लॉक", "विंग"],
  lift: ["लिफ्ट", "लिफ्ट"], elevator: ["लिफ्ट", "लिफ्ट"], stuck: ["फंसी", "अडकली"], broken: ["टूटा हुआ", "तुटलेले"], stopped: ["बंद", "बंद"], working: ["काम कर रहा", "कार्यरत"],
  electricity: ["बिजली", "वीज"], electric: ["बिजली", "वीज"], power: ["बिजली", "वीज"], light: ["बत्ती", "दिवा"], lights: ["बत्तियाँ", "दिवे"],
  garbage: ["कचरा", "कचरा"], waste: ["कचरा", "कचरा"], dirty: ["गंदा", "अस्वच्छ"], smell: ["दुर्गंध", "दुर्गंधी"], cleaning: ["सफाई", "स्वच्छता"],
  road: ["सड़क", "रस्ता"], pothole: ["गड्ढा", "खड्डा"], potholes: ["गड्ढे", "खड्डे"], crack: ["दरार", "भेग"], cracks: ["दरारें", "भेगा"],
  parking: ["पार्किंग", "पार्किंग"], vehicle: ["वाहन", "वाहन"], unauthorized: ["अनधिकृत", "अनधिकृत"], security: ["सुरक्षा", "सुरक्षा"], guard: ["सुरक्षा कर्मी", "सुरक्षा रक्षक"], camera: ["कैमरा", "कॅमेरा"],
  noise: ["शोर", "आवाज"], loud: ["तेज़", "मोठा"], dog: ["कुत्ता", "कुत्रा"], dogs: ["कुत्ते", "कुत्रे"], mosquito: ["मच्छर", "डास"], mosquitoes: ["मच्छर", "डास"], pest: ["कीट", "कीड"],
  problem: ["समस्या", "समस्या"], issue: ["समस्या", "समस्या"], complaint: ["शिकायत", "तक्रार"], damage: ["नुकसान", "नुकसान"], damaged: ["क्षतिग्रस्त", "नुकसान झालेले"], danger: ["खतरा", "धोका"], dangerous: ["खतरनाक", "धोकादायक"], safety: ["सुरक्षा", "सुरक्षा"],
  urgent: ["तत्काल", "तातडीचे"], urgently: ["तुरंत", "तातडीने"], repair: ["मरम्मत", "दुरुस्ती"], inspect: ["जाँच करें", "तपासणी करा"], inspection: ["जाँच", "तपासणी"], resolve: ["समाधान करें", "सोडवा"], fix: ["ठीक करें", "दुरुस्त करा"],
  please: ["कृपया", "कृपया"], immediately: ["तुरंत", "तात्काळ"], causing: ["कारण बन रहा", "कारणीभूत ठरत आहे"], caused: ["कारण बना", "कारणीभूत ठरले"], residents: ["निवासियों", "रहिवाशांना"], resident: ["निवासी", "रहिवासी"], common: ["सामुदायिक", "सामायिक"], area: ["क्षेत्र", "भाग"],
};

const devanagariLetters: Record<string, string> = {
  a: "अ", b: "ब", c: "क", d: "द", e: "ए", f: "फ", g: "ग", h: "ह", i: "इ", j: "ज", k: "क", l: "ल", m: "म",
  n: "न", o: "ओ", p: "प", q: "क", r: "र", s: "स", t: "त", u: "उ", v: "व", w: "व", x: "क्स", y: "य", z: "ज़",
};

function transliterateUnknownWord(word: string) {
  if (/^[A-Z]$/.test(word) || /^[A-Z]{1,3}\d+$/.test(word)) return word;
  return word.toLowerCase().split("").map((letter) => devanagariLetters[letter] ?? letter).join("");
}

function translateDynamicWords(text: string, language: Exclude<AppLanguage, "en">) {
  return text.replace(/[A-Za-z][A-Za-z'-]*/g, (word) => {
    const localized = societyWords[word.toLowerCase()];
    if (localized) return localized[language === "hi" ? 0 : 1];
    return transliterateUnknownWord(word);
  }).replace(/\s{2,}/g, " ").replace(/\s+([,.;:!?])/g, "$1").trim();
}

export function translateSocietyText(text: string, language: AppLanguage) {
  if (language === "en" || !text.trim()) return text;
  const exact = words[text]?.[language];
  if (exact) return exact;
  const caseInsensitiveKey = caseInsensitiveWords.get(text.toLocaleLowerCase("en-IN"));
  if (caseInsensitiveKey) return words[caseInsensitiveKey][language];

  const activeCount = text.match(/^Active \((\d+)\)$/i);
  if (activeCount)
    return language === "hi" ? `सक्रिय (${activeCount[1]})` : `सक्रिय (${activeCount[1]})`;
  const complaintNumber = text.match(/^Complaint #(\d+)$/i);
  if (complaintNumber)
    return language === "hi" ? `शिकायत #${complaintNumber[1]}` : `तक्रार #${complaintNumber[1]}`;

  let translated = text;
  const interfaceParts = language === "hi"
    ? [["Flat", "फ्लैट"], ["Floor", "मंजिल"], ["Reported", "दर्ज"]]
    : [["Flat", "फ्लॅट"], ["Floor", "मजला"], ["Reported", "नोंद"]];
  for (const [english, localized] of interfaceParts)
    translated = translated.replace(new RegExp(`\\b${english}\\b`, "gi"), localized);

  if (!societyContentMarker.test(text)) return translated;
  for (const [english, hindi, marathi] of societyPhrases) {
    const escaped = english.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    translated = translated.replace(
      new RegExp(escaped, "gi"),
      language === "hi" ? hindi : marathi,
    );
  }
  return translated;
}

export function translateDynamicSocietyText(text: string, language: AppLanguage) {
  if (language === "en" || !text.trim()) return text;
  const exact = words[text]?.[language];
  if (exact) return exact;
  const caseInsensitiveKey = caseInsensitiveWords.get(text.toLocaleLowerCase("en-IN"));
  if (caseInsensitiveKey) return words[caseInsensitiveKey][language];
  let translated = text;
  for (const [english, hindi, marathi] of societyPhrases) {
    const escaped = english.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    translated = translated.replace(new RegExp(escaped, "gi"), language === "hi" ? hindi : marathi);
  }
  return translateDynamicWords(translated, language);
}

export function useI18n() {
  const language = useLanguageStore((state) => state.language);
  return { language, t: (text: string) => translateSocietyText(text, language) };
}
