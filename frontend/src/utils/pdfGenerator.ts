import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export const generateReportPDF = async (reportTitle: string, contentElementId: string = 'report-content') => {
  try {
    // Get the report content element
    const reportElement = document.getElementById(contentElementId);

    if (!reportElement) {
      console.error('Report content element not found');
      return;
    }

    // Hide buttons and interactive elements before capture
    const buttons = reportElement.querySelectorAll('button');
    buttons.forEach(btn => {
      (btn as HTMLElement).style.display = 'none';
    });

    // Capture the content as canvas with high quality
    const canvas = await html2canvas(reportElement, {
      scale: 2, // Higher quality
      useCORS: true,
      logging: false,
      backgroundColor: '#F7FAFC',
      windowWidth: reportElement.scrollWidth,
      windowHeight: reportElement.scrollHeight
    });

    // Restore buttons
    buttons.forEach(btn => {
      (btn as HTMLElement).style.display = '';
    });

    // Calculate PDF dimensions
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;

    // Create PDF
    const pdf = new jsPDF('p', 'mm', 'a4');
    let position = 0;

    // Add image to PDF
    const imgData = canvas.toDataURL('image/png');
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // Add new pages if content is longer than one page
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    // Generate filename with timestamp
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${reportTitle.replace(/\s+/g, '_')}_${timestamp}.pdf`;

    // Save the PDF
    pdf.save(filename);

    console.log('PDF generated successfully:', filename);
  } catch (error) {
    console.error('Error generating PDF:', error);
    alert('Failed to generate PDF. Please try again.');
  }
};

// Alternative: Generate PDF with better page breaks
export const generateReportPDFAdvanced = async (reportTitle: string) => {
  try {
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    // Add header
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text(reportTitle, 15, 20);

    // Add generation date
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    const date = new Date().toLocaleDateString();
    pdf.text(`Generated on: ${date}`, 15, 30);

    // Add a separator line
    pdf.setLineWidth(0.5);
    pdf.line(15, 35, pageWidth - 15, 35);

    // Capture main content
    const reportElement = document.getElementById('report-content');
    if (reportElement) {
      const canvas = await html2canvas(reportElement, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#F7FAFC'
      });

      const imgData = canvas.toDataURL('image/png');
      const imgWidth = pageWidth - 30; // margins
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      pdf.addImage(imgData, 'PNG', 15, 40, imgWidth, imgHeight);
    }

    // Save PDF
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `${reportTitle.replace(/\s+/g, '_')}_${timestamp}.pdf`;
    pdf.save(filename);

    console.log('Advanced PDF generated successfully:', filename);
  } catch (error) {
    console.error('Error generating advanced PDF:', error);
    alert('Failed to generate PDF. Please try again.');
  }
};
