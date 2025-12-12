using System.Collections;
using System.Net;
using UnityEngine;
using UnityEngine.Networking;
using static System.Runtime.CompilerServices.RuntimeHelpers;

public class VoiceManager : MonoBehaviour
{
    private AudioClip recording;
    private string microphoneDevice;
    private bool isRecording = false;

    //buraya backend url adresi gelecek
    private string backendUrl = "websocketbridge.duckdns.org/voice-message";

    void Start()
    {
        // İlk mikrofonu seç
        if (Microphone.devices.Length > 0)
        {
            microphoneDevice = Microphone.devices[0];
        }
        else
        {
            Debug.LogError("Mikrofon bulunamadı!");
        }
    }

    void Update()
    {
        // V tuşuna basınca kaydı başlat
        if (Input.GetKeyDown(KeyCode.V) && !isRecording)
        {
            StartRecording();
        }

        // V tuşunu bırakınca kaydı durdur ve gönder
        if (Input.GetKeyUp(KeyCode.V) && isRecording)
        {
            StopRecordingAndSend();
        }
    }

    void StartRecording()
    {
        isRecording = true;
        // Maksimum 10 saniyelik, 44100 Hz örnekleme hızıyla kayıt
        recording = Microphone.Start(microphoneDevice, false, 10, 44100);
        Debug.Log("Kayıt Başladı...");
    }

    void StopRecordingAndSend()
    {
        isRecording = false;
        Microphone.End(microphoneDevice);
        Debug.Log("Kayıt Bitti, sunucuya gönderiliyor...");

        // Sesi WAV formatına çevir (SavWav kütüphanesi veya manuel byte dönüştürme gerekir)
        // Kolaylık olması için basit bir byte array gönderimi yapıyoruz:
        byte[] audioBytes = WavUtility.FromAudioClip(recording);

        StartCoroutine(SendAudioToBackend(audioBytes));
    }

    IEnumerator SendAudioToBackend(byte[] audioData)
    {
        WWWForm form = new WWWForm();
        form.AddBinaryData("file", audioData, "recording.wav", "audio/wav");

        using (UnityWebRequest www = UnityWebRequest.Post(backendUrl, form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Hata: " + www.error);
            }
            else
            {
                string jsonResponse = www.downloadHandler.text;
                Debug.Log("Sunucu Cevabı: " + jsonResponse);

                // Gelen komutu işle
                ProcessCommand(jsonResponse);
            }
        }
    }

    void ProcessCommand(string json)
    {
        // Burada gelen JSON'ı parse edip (JsonUtility kullanarak) eyleme dökeceksiniz.
        // Örnek: {"action": "open_ac"}
        Debug.Log("Eylem gerçekleştiriliyor" + json);

        // Basit bir örnek parse (daha sağlam bir JSON yapısı kurmalısınız)
        if (json.Contains("klima_ac"))
        {
            // Klima açma fonksiyonunu çağır
            Debug.Log("Klima Açıldı!");
        }
        else if (json.Contains("klima_kapat"))
        {
            Debug.Log("Klima kapandı!");
        }
        else if (json.Contains("isik_ac"))
        {
            Debug.Log("Işıklar açıldı");
        }
        else if (json.Contains("make_coffe"))
        {
            Debug.Log("Kahve yapılıyor");
        }
        else if (json.Contains("Turn_on_music"))
        {
            Debug.Log("Müzik açıldı!");
        }
        else if (json.Contains("Turn_off_music"))
        {
            Debug.Log("Müzik kapandı!");
        }
        else if (json.Contains("isik_kapat"))
        {
            // Işık kapatma fonksiyonunu çağır
            Debug.Log("Işıklar Kapandı!");
        }
    }
}