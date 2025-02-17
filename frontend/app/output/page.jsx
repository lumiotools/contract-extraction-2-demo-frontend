"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import dummyTable from "@/constants/dummyTable.json";

export default function OutputPage() {
  return (
    <div className="min-h-screen bg-[#1C1C28] flex items-center justify-center w-full p-8">
      <div className="max-w-4xl w-full">
        <Card className="bg-[#2A2A36] border-gray-700 rounded-xl mb-8">
          <CardHeader>
            <CardTitle className="text-white">Service Discounts and Spend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Service</TableHead>
                    <TableHead>Average Discount (%)</TableHead>
                    <TableHead>Total Spend ($)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {dummyTable.map((row, index) => (
                    <TableRow key={index}>
                      <TableCell>{row.Service}</TableCell>
                      <TableCell>{row["Average Discount (%)"]}</TableCell>
                      <TableCell>{row["Total Spend ($)"]}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}