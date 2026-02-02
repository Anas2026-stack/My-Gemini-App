import streamlit as st
import google.generativeai as genai
import importlib.metadata

st.set_page_config(page_title="System Check", layout="wide")
st.title("🛠️ غرفة الصيانة وكشف الأخطاء")

# 1. كشف إصدار المكتبة (هل تم التحديث؟)
try:
    lib_version = importlib.metadata.version("google-generativeai")
    st.write(f"### 1️⃣ إصدار المكتبة المثبت حالياً: `{lib_version}`")
    
    # نحتاج نسخة 0.5.0 أو أعلى ليعمل 1.5
    if lib_version < "0.5.0":
        st.error("⛔ كارثة: السيرفر لا يزال يستخدم نسخة قديمة! التحديث لم يطبق.")
    else:
        st.success("✅ ممتاز: المكتبة محدثة وتدعم Gemini 1.5.")
except:
    st.warning("⚠️ تعذر تحديد الإصدار.")

# 2. فحص المفاتيح
api_keys = [v for k, v in st.secrets.items() if k.startswith("KEY_")]
if not api_keys:
    st.error("❌ المفاتيح مفقودة في Secrets!")
    st.stop()
else:
    st.success(f"✅ تم العثور على {len(api_keys)} مفتاح.")

# 3. سرد الموديلات المتاحة (الحقيقة الكاملة)
st.write("### 2️⃣ الموديلات المسموح لك باستخدامها:")
try:
    genai.configure(api_key=api_keys[0])
    
    my_models = []
    # نجلب القائمة من جوجل مباشرة
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            my_models.append(m.name)
    
    if not my_models:
        st.error("لم يتم العثور على أي موديل! قد تكون المشكلة في المفتاح أو الدولة.")
    else:
        # عرض القائمة في صندوق اختيار
        selected_model = st.selectbox("اختر موديلاً من القائمة المتاحة (الموثقة):", my_models)
        st.info(f"💡 نصيحة: عادة يكون اسمه `models/gemini-1.5-flash` أو `models/gemini-pro`")

        # 4. تجربة حية
        if st.button("🔴 اضغط هنا لاختبار الموديل المختار"):
            with st.spinner("جاري الاتصال..."):
                try:
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content("هل تعمل؟ أجب بكلمة واحدة: نعم.")
                    st.success(f"🎉 النتيجة: {response.text}")
                    st.balloons()
                except Exception as e:
                    st.error(f"فشل الاختبار: {e}")

except Exception as e:
    st.error(f"حدث خطأ أثناء الاتصال بجوجل: {e}")
