"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import dummyTable1 from "@/constants/dummyTable1.json";
import dummyTable2 from "@/constants/dummyTable2.json";

export default function OutputPage() {
  const [annualSpend, setAnnualSpend] = useState("");
  const [showTables, setShowTables] = useState(false);

  const handleInputChange = (e) => {
    setAnnualSpend(e.target.value);
  };

  const handleButtonClick = () => {
    setShowTables(true);
  };

  return (
    <div className="min-h-screen bg-[#1C1C28] flex items-center justify-center w-full p-8">
      <div className="max-w-4xl w-full">
        <Card className="bg-[#2A2A36] border-gray-700 rounded-xl mb-8">
          <CardHeader>
            <CardTitle className="text-white">Annual Spend</CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              type="text"
              placeholder="Annual Spend in $"
              value={annualSpend}
              onChange={handleInputChange}
              className="mb-4"
            />
            <Button onClick={handleButtonClick} className="bg-orange-500 hover:bg-orange-600 text-black">
              Submit
            </Button>
          </CardContent>
        </Card>

        {showTables && (
          <>
            <Card className="bg-[#2A2A36] border-gray-700 rounded-xl mb-8">
              <CardHeader>
                <CardTitle className="text-white">Table 1: Average Discount</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Service</TableHead>
                        <TableHead>Average Discount (in %)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {dummyTable1.map((row, index) => (
                        <TableRow key={index}>
                          <TableCell>{row.Service}</TableCell>
                          <TableCell>{row["Average Discount (in %)"]}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-[#2A2A36] border-gray-700 rounded-xl">
              <CardHeader>
                <CardTitle className="text-white">Table 2: Total Spend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Service</TableHead>
                        <TableHead>Total Spend ($)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {dummyTable2.map((row, index) => (
                        <TableRow key={index}>
                          <TableCell>{row.Service}</TableCell>
                          <TableCell>{row["Total Spend ($)"]}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}