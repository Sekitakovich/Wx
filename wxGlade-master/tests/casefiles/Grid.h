// -*- C++ -*-
//
// generated by wxGlade
//
// Example for compiling a single file project under Linux using g++:
//  g++ MyApp.cpp $(wx-config --libs) $(wx-config --cxxflags) -o MyApp
//
// Example for compiling a multi file project under Linux using g++:
//  g++ main.cpp $(wx-config --libs) $(wx-config --cxxflags) -o MyApp Dialog1.cpp Frame1.cpp
//

#ifndef GRID_H
#define GRID_H

#include <wx/wx.h>
#include <wx/image.h>

// begin wxGlade: ::dependencies
#include <wx/grid.h>
// end wxGlade

// begin wxGlade: ::extracode
// end wxGlade


class MyFrame: public wxFrame {
public:
    // begin wxGlade: MyFrame::ids
    // end wxGlade

    MyFrame(wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos=wxDefaultPosition, const wxSize& size=wxDefaultSize, long style=wxDEFAULT_FRAME_STYLE);

private:

protected:
    // begin wxGlade: MyFrame::attributes
    wxGrid* grid_1;
    // end wxGlade

    DECLARE_EVENT_TABLE();

public:
    virtual void myEVT_GRID_CELL_LEFT_CLICK(wxGridEvent &event); // wxGlade: <event_handler>
}; // wxGlade: end class


#endif // GRID_H
