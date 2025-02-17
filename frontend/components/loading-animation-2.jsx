import React from "react";
import { Card } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

export function LoadingAnimation2() {
  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-[#1C1C28]/80 backdrop-blur-md" />
      <div className="relative h-full flex items-center justify-center">
        <Card className="w-full max-w-md mx-auto bg-[#23232F]/90 border-[#2A2A36]">
          <div className="p-8 flex flex-col items-center space-y-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/30 to-orange-500/30 blur-xl rounded-full" />
              <Loader2 className="w-16 h-16 text-orange-500 animate-spin relative z-10" />
            </div>

            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-white">
                Analyzing Shipment Details
              </h2>
              <p className="text-sm text-gray-400">
                This may take up to 20 seconds
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
