import unittest
from unittest.mock import MagicMock, patch
import json
import os
import sys

# Ensure main is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestResumeCustomizer(unittest.TestCase):
    
    @patch('main.API_KEY', 'TEST_KEY')
    @patch('main.storage')
    @patch('main.genai')
    @patch('main.pypdf')
    def test_signature_fallback(self, mock_pypdf, mock_genai, mock_storage):
        """
        Test that the signature is appended if missing from the Gemini response.
        """
        import main
        
        # 1. Setup Request
        mock_request = MagicMock()
        mock_request.get_json.return_value = {
            "job_description": "We need a python dev.",
            "job_url": None
        }
        
        # 2. Mock GCS
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage.Client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # 3. Mock PDF Reader
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Old Resume Text"
        mock_reader.pages = [mock_page]
        mock_pypdf.PdfReader.return_value = mock_reader

        # 4. Mock Gemini Response (MISSING SIGNATURE)
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        response_content = {
            "company": "Tech Corp",
            "job_title": "Python Developer",
            "cover_letter_text": "Dear Hiring Manager,\n\nI love code.\n\nBest regards,\n[Missing Name]",
            "resume_data": {
                "contact_info": {"name": "Tommy Delta"},
                "summary": "Summary",
                "skills": "Python"
            }
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_content)
        mock_model.generate_content.return_value = mock_response

        # 5. Run
        response_body, status_code, headers = main.customize_resume(mock_request)
        
        # 6. Verify
        if status_code != 200:
            print(f"Test Failed with 500: {response_body}")
            
        self.assertEqual(status_code, 200)

    @patch('main.API_KEY', 'TEST_KEY')
    @patch('main.Document')
    @patch('main.storage')
    @patch('main.genai')
    @patch('main.pypdf')
    def test_signature_enforcement(self, mock_pypdf, mock_genai, mock_storage, mock_document):
        import main
        
        mock_request = MagicMock()
        mock_request.get_json.return_value = {"job_description": "job"}
        
        # Mock PDF
        mock_pypdf.PdfReader.return_value.pages = [MagicMock(extract_text=lambda: "resume")]
        mock_storage.Client.return_value.bucket.return_value.blob.return_value = MagicMock()

        # Mock Gemini Response
        mock_response_text = {
            "cover_letter_text": "Ending without signature.",
            "resume_data": {}
        }
        mock_genai.GenerativeModel.return_value.generate_content.return_value.text = json.dumps(mock_response_text)
        
        main.customize_resume(mock_request)
            
        # Verify Document calls
        doc_instance = mock_document.return_value
        calls = doc_instance.add_paragraph.call_args_list
        
        found_signature = False
        full_text_sent = ""
        
        for call in calls:
            args, _ = call
            if args:
                text = args[0]
                if "Ending without signature." in text:
                    full_text_sent = text
                    if "Tommy Delta" in text:
                        found_signature = True
        
        self.assertTrue(found_signature, f"Signature not found in text passed to Document: '{full_text_sent}'")

if __name__ == '__main__':
    unittest.main()
