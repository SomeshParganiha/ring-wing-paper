// Vyoma ring-wing viewer for OpenSCAD
// -----------------------------------
// Open this file in OpenSCAD and press F5 (preview).
// The STL must sit in the same folder as this .scad file.
//
// Model: superellipse p=4 ring (span 36 m, height 18 m, h/b = 0.5),
// NACA 0012 sections, chord 3.6 m, staggered arcs, lifting-body cabin
// low in the ring. Units are metres at full scale.

// ---- choose ONE mode ----
full_scale   = true;   // true: metres (36 units span)
print_model  = false;  // true: 180 mm span desk/3D-print model

if (full_scale)
    import("vyoma.stl", convexity = 10);

if (print_model)
    scale(0.005)   // 36 m span -> 180 mm desk model
    import("vyoma.stl", convexity = 10);
