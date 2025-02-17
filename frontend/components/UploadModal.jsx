import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UploadIcon, Loader2 } from "lucide-react";
import { LoadingAnimation2 } from "@/components/loading-animation-2";

export default function UploadModal({ isOpen, onClose, onUpload }) {
  const [file, setFile] = useState(null);
  const [isUploaded, setIsUploaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setIsUploaded(true);
    }
  };

  const handleUpload = async () => {
    if (file) {
      setLoading(true);
      // Simulate a delay of up to 20 seconds
      await new Promise((resolve) => setTimeout(resolve, 20000));
      onUpload(file);
      setLoading(false);
      onClose();
    } else {
      setErrors({ file: "Please upload an Excel file" });
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {loading && <LoadingAnimation2 />}
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="bg-[#2A2A36] p-6 rounded-lg border border-gray-700 w-96">
          <h2 className="text-xl font-bold mb-4 text-white">Upload Shipment History</h2>
          <Label htmlFor="excelFile" className="text-base text-gray-300 mb-2 block">
            Format: XLSX
          </Label>
          <div className="relative">
            <label
              htmlFor="excelFile"
              className={`flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl cursor-pointer transition-colors ${
                isUploaded
                  ? "border-green-500 bg-green-500/10"
                  : "border-gray-600 hover:bg-[#2A2A36]"
              }`}
            >
              <div className="flex flex-col items-center justify-center py-4">
                {isUploaded ? (
                  <>
                    <UploadIcon className="w-10 h-10 mb-2 text-green-500" />
                    <p className="text-sm text-green-500">File uploaded successfully</p>
                  </>
                ) : (
                  <>
                    <UploadIcon className="w-10 h-10 mb-2 text-orange-500" />
                    <p className="text-sm text-gray-400">
                      <span className="font-semibold text-orange-500">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 mt-1">XLSX (MAX. 10MB)</p>
                  </>
                )}
              </div>
              <Input
                id="excelFile"
                type="file"
                accept=".xlsx"
                className="hidden"
                onChange={handleFileChange}
              />
            </label>
            {errors.file && (
              <p className="text-red-500 text-sm mt-1">{errors.file}</p>
            )}
          </div>
          <div className="mt-4 flex justify-end space-x-2">
            <Button onClick={onClose} className="bg-gray-500 hover:bg-gray-600 text-white">
              Cancel
            </Button>
            <Button onClick={handleUpload} className="bg-orange-500 hover:bg-orange-600 text-black" disabled={loading}>
              {loading ? <Loader2 className="animate-spin mr-2" /> : "Upload"}
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}